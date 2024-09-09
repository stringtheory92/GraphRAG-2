interface Document {
  content: string;
}

const documents: Document[] = [
  {
    content: `Influencer: Hey everyone, thanks for joining me today. I'm excited to answer some of your questions. Let's get started!

User Question: What's the best way to grow my Instagram following?
Influencer: The best way to grow your Instagram following is to consistently post high-quality, engaging content. Make sure you're using relevant hashtags and tagging people/brands in your posts. Interact with your followers by responding to comments and liking their posts. You should also try to collaborate with other creators in your niche.

User Question: How do I get started with affiliate marketing?
Influencer: Affiliate marketing is a great way to monetize your audience. Start by researching products or services that align with your niche and audience. Reach out to those brands and see if they have an affiliate program. Once you're accepted, start promoting those products to your followers. Make sure you disclose that the links are affiliate links. Over time, as you build trust with your audience, you can earn commissions from sales.`,
  },
  {
    content: `Influencer: Hi everyone, thanks for tuning in. I'm excited to answer your questions today.

User Question: What's the best way to overcome imposter syndrome as a creator?
Influencer: Imposter syndrome is something a lot of creators struggle with. The best way to overcome it is to focus on your progress and achievements, rather than comparing yourself to others. Celebrate your small wins and remind yourself of how far you've come. It's also helpful to surround yourself with a supportive community of other creators who can relate to what you're going through.

User Question: How do I find my niche as a content creator?
Influencer: Finding your niche is so important as a content creator. Start by thinking about your passions and interests. What topics do you love to learn about and talk about? Then, research to see if there's an audience for that content. Look at what other creators are doing in that space. Try out different types of content and see what resonates best with your audience. Over time, you'll naturally start to hone in on your unique niche.`,
  },
  {
    content: `Influencer: Thanks everyone for joining me today. I'm excited to dive into your questions.

User Question: How do I stay motivated and consistent with content creation?
Influencer: Staying motivated and consistent with content creation can be really challenging. The key is to find ways to make it fun and rewarding for you. Set achievable goals, celebrate your wins, and don't be too hard on yourself when you miss a post. It also helps to batch content creation so you're not always feeling the pressure to come up with new ideas. And don't forget to take breaks when you need them - self-care is so important for creators.

User Question: What are some tips for growing my email list as a creator?
Influencer: Growing your email list is crucial as a creator. Offer valuable lead magnets like ebooks, checklists, or exclusive content in exchange for an email address. Make sure your signup forms are visible and easy to find on your website and social channels. Promote your list-building incentives consistently. You can also collaborate with other creators to cross-promote to each other's audiences. The key is providing so much value that people are eager to join your email list.`,
  },
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
  const lines = relevantContent.split("\n");
  const response = lines.find(
    (line) =>
      line.startsWith("Influencer:") &&
      line.toLowerCase().includes(prompt.toLowerCase())
  );

  if (response) {
    return response.replace("Influencer:", "").trim();
  } else {
    return "I'm sorry, I couldn't find a specific answer to your question. Could you please rephrase or ask about a different topic?";
  }
}
