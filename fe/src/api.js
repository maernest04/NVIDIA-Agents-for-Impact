/**
 * Send a user message to the backend agent and stream the response via SSE.
 *
 * @param {string} message - The user's current message.
 * @param {Array<{role: string, content: string}>} history - Prior conversation turns.
 * @param {(event: object) => void} onEvent - Called for each SSE event:
 *   { type: 'tool_call', tool: string }
 *   { type: 'categories', categories: string[] }
 *   { type: 'token', content: string }
 *   { type: 'done' }
 *   { type: 'error', message: string }
 */
export async function sendChatMessage(message, history = [], onEvent) {
  const res = await fetch('/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE events are separated by double newlines
    const parts = buffer.split('\n\n');
    buffer = parts.pop(); // keep any incomplete trailing chunk

    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith('data: ')) continue;
      try {
        const event = JSON.parse(line.slice(6));
        onEvent(event);
      } catch {
        // skip malformed events
      }
    }
  }
}

/**
 * Fetch campus resources, optionally filtered by keyword.
 * @param {string} [search] - Optional search keyword.
 * @returns {Promise<Array>} - Array of resource objects.
 */
export async function fetchResources(search) {
  const url = new URL('/resources/', window.location.origin);
  if (search) url.searchParams.set('search', search);

  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch resources: ${res.status}`);
  return res.json();
}
