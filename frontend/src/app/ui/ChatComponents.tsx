'use client';

import { useState } from "react";

type Message = {
  message: string,
  fromUser?: boolean
}

export default function ChatBox () {
  const [messages, setMessages] = useState<Message[]>([]);
  
  function addMessage(message: string, fromUser: boolean) {
    setMessages(prevMessages => [...prevMessages, {message, fromUser}]);
  }

  return (
    <div className="grid grid-rows-[auto_5rem] h-screen justify-center py-10">
      <div className="bg-gray-500 h-full rounded-2xl p-5">
        {messages.map((message, idx) => {
           return <ChatBubble messageObject={message} key={idx}/>;
        })}
      </div>
      <ChatBar addMessage={addMessage}/>
    </div>
  );
}

export function ChatBar ({ addMessage } : { addMessage: (message: string, fromUser: boolean) => void}) {
  const [input, setInput] = useState("")

  function handlePrompt (eventObject: React.FormEvent<HTMLFormElement>) {
    eventObject.preventDefault();

    console.log(input);

    addMessage(input, true);
    setInput("");
  }

  return (
      <div className="">
          <label htmlFor="user-input" className="sr-only">
              Enter prompt.
          </label>
          <form className="flex flex-row items-center mt-5" onSubmit={handlePrompt}>
              <input onChange={e => setInput(e.target.value)} value={input} name="prompt" placeholder="Ask a question" id="user-input" className="bg-white w-[55rem] rounded-2xl mr-5 text-black p-3" type="text"/>
              <button className="bg-black rounded-2xl p-1 hover:bg-gray-700 active:bg-gray-500 transition">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3" />
                  </svg>
              </button>
          </form>
      </div>
  );
}

export function ChatBubble({ messageObject }: {messageObject: Message} ) {
  return (
    <div className={`flex ${messageObject.fromUser ? 'justify-end' : 'justify-start'} mb-2`}>
      <div
        className={`max-w-xs px-4 py-2 rounded-2xl text-sm
          ${messageObject.fromUser
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-gray-200 text-black rounded-bl-none'
          }`}
      >
        {messageObject.message}
      </div>
    </div>
  );
}