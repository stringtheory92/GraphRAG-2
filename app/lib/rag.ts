interface Document {
  content: string;
}

const documents: Document[] = [
  {
    content: `Your custom document content here.`
  },
  // Add more documents as needed
];

function findRelevantDocument(query: string): string {
  const lowercaseQuery = query.toLowerCase();
  for (const doc of documents) {
    if (doc.content.toLowerCase().includes(lowercaseQuery)) {
      return doc.content;
    }
  }
  return "I'm sorry, I don't have information about that topic in my knowledge base.";
}

export function generateResponse(prompt: string): string {
  const relevantContent = findRelevantDocument(prompt);
  const lines = relevantContent.split('\n');
  const response = lines.find(line => line.startsWith('Influencer:') && line.toLowerCase().includes(prompt.toLowerCase()));
  
  if (response) {
    return response.replace('Influencer:', '').trim();
  } else {
    return "I'm sorry, I couldn't find a specific answer to your question. Could you please rephrase or ask about a different topic?";
  }
}
