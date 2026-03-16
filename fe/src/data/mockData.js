export const mockCategories = [
  { id: 'mental_health', label: 'Mental Health' },
  { id: 'suicide', label: 'Suicide Risk' },
  { id: 'domestic_violence', label: 'Domestic Violence' },
  { id: 'substance_use', label: 'Substance Use' },
  { id: 'homelessness', label: 'Housing / Homelessness' },
  { id: 'human_trafficking', label: 'Human Trafficking' },
  { id: 'general_crisis', label: 'General Crisis' },
  { id: 'emergency', label: 'Immediate Emergency' }
];

export const mockResources = [
  {
    id: '988',
    name: '988 Suicide & Crisis Lifeline',
    phone: '988',
    url: 'https://988lifeline.org',
    availability: 'Available 24/7. Free and confidential.',
    whyItHelps: 'They provide free, confidential support for people in distress, as well as prevention and crisis resources.',
    callScript: "Hi, I'm going through a hard time and need support right now. I don't know exactly what to say, but I could use someone to talk to."
  },
  {
    id: 'ctl',
    name: 'Crisis Text Line',
    phone: 'Text HOME to 741741',
    url: 'https://www.crisistextline.org',
    availability: 'Available 24/7. Free and confidential.',
    whyItHelps: 'Connect with a volunteer Crisis Counselor over text message. It can be easier if you are in a situation where you cannot safely talk out loud.',
    callScript: "HOME"
  },
  {
    id: 'ndvh',
    name: 'National Domestic Violence Hotline',
    phone: '1-800-799-SAFE (7233)',
    url: 'https://www.thehotline.org',
    availability: 'Available 24/7. Free and confidential.',
    whyItHelps: 'They can help you safely navigate your current living situation and connect you with local shelters or resources.',
    callScript: "Hi, I'm deeply concerned about my safety at home and need advice on what options I might have."
  }
];

export const promptChips = [
  "I'm feeling overwhelmed",
  "I don't feel safe at home",
  "I need mental health support",
  "I'm worried about a friend",
  "I need help tonight",
  "I don't know where to start"
];
