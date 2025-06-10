import { useState } from "react";

import { Attempt, Message, Query } from "api";

import { Chat } from "../ui/chat";
import { Message as ChatMessage } from "../ui/chat-message";

type AssistantProps = {
  query: Query | Attempt;
  sendMessageApi: (args: {
    id: number;
    requestBody: Message;
  }) => Promise<Message>;
};

const Assistant = ({ query, sendMessageApi }: AssistantProps) => {
  const toChatMessage = ({ id, content, author }: Message): ChatMessage => ({
    id: id.toString(),
    content,
    role: author,
  });

  const [messages, setMessages] = useState<ChatMessage[]>(
    query.assistant_messages.map((message) => toChatMessage(message)),
  );
  const [input, setInput] = useState<string>("");
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const addMessage = (message: Message) => {
    setMessages((prevMessages) => [...prevMessages, toChatMessage(message)]);
  };

  const sendMessage = async (message: string) => {
    addMessage({ id: 0, content: message, author: "user" } as Message);
    setIsGenerating(true);
    const reply = await sendMessageApi({
      id: query.id,
      requestBody: {
        content: input,
      } as Message,
    });
    setIsGenerating(false);
    addMessage(reply);
  };

  const handleSubmit = (event?: { preventDefault?: () => void }) => {
    event?.preventDefault?.();
    sendMessage(input);
    setInput("");
  };

  return (
    <Chat
      className="mx-3 flex-1 min-h-0"
      handleInputChange={(e) => {
        setInput(e.target.value);
      }}
      handleSubmit={handleSubmit}
      input={input}
      isGenerating={isGenerating}
      messages={messages}
    />
  );
};

export default Assistant;
