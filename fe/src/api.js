const API_BASE = 'http://localhost:8000';

/**
 * Send a user message to the backend agent with conversation history.
 * @param {string} message - The user's current message text.
 * @param {Array<{role: string, content: string}>} history - Previous messages.
 * @returns {Promise<string>} - The AI agent's response text.
 */
export async function sendChatMessage(message, history = []) {
  const res = await fetch(`${API_BASE}/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${res.status}`);
  }

  const data = await res.json();
  return data.response;
}

/**
 * Fetch campus resources, optionally filtered by keyword.
 * @param {string} [search] - Optional search keyword.
 * @returns {Promise<Array>} - Array of resource objects.
 */
export async function fetchResources(search) {
  const url = new URL(`${API_BASE}/resources/`);
  if (search) url.searchParams.set('search', search);

  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch resources: ${res.status}`);
  return res.json();
}
