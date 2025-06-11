import { useEffect, useState } from "react";

import { Attempt, Message, Query } from "api";

import { Chat } from "../ui/chat";
import { Message as ChatMessage } from "../ui/chat-message";

type AssistantProps = {
  query: Query | Attempt;
  sendMessageApi: (args: {
    id: number;
    requestBody: Message;
  }) => Promise<Message>;
  suggestions?: string[];
  onUnmount?: () => Promise<void>;
};

const Assistant = ({
  query,
  sendMessageApi,
  onUnmount,
  suggestions = [],
}: AssistantProps) => {
  const toChatMessage = ({ id, content, author }: Message): ChatMessage => ({
    id: id.toString(),
    content,
    role: author,
  });

  const [messages, setMessages] = useState<ChatMessage[]>(
    query.assistant_messages.map((message) => toChatMessage(message)),
  );

  useEffect(() => {
    return () => {
      onUnmount?.();
    };
  }, [onUnmount]);

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
        content: message,
      } as Message,
    });
    setIsGenerating(false);
    addMessage(reply);
  };

  const handleSuggestionClick = ({
    content,
  }: {
    role: "user";
    content: string;
  }) => {
    sendMessage(content);
  };

  const handleSubmit = (event?: { preventDefault?: () => void }) => {
    event?.preventDefault?.();
    sendMessage(input);
    setInput("");
  };

  return (
    <Chat
      append={handleSuggestionClick}
      className="mx-3 flex-1 min-h-0"
      handleInputChange={(e) => {
        setInput(e.target.value);
      }}
      handleSubmit={handleSubmit}
      input={input}
      isGenerating={isGenerating}
      messages={messages}
      suggestions={[
        ...suggestions,
        "How can I improve my query?",
        "Why is this query giving the wrong result?",
      ]}
    />
  );
};

export default Assistant;
