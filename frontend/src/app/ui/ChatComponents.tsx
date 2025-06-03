'use client';

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

type Message = {
  text: string,
  fromUser?: boolean
}

export default function ChatBox () {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({block: 'end', behavior:'smooth'});
      console.log("Scrolling into view.");
    }
  })

  async function sendPrompt (msg: Message): Promise<Message> {
    setLoading(true);

    const response = await fetch("http://127.0.0.1:8000/prompt", {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ text: msg.text }),
    });
    const responseText = await response.json();
    const msgObject = {
      text: responseText.message,
      fromUser: false
    }
    setLoading(false);
    return msgObject;
  }
  
  async function addMessage(messageTxt: string, fromUserValue: boolean) {
    
    const msgObject = { 
      text: messageTxt,
      fromUser: fromUserValue
    }

    setMessages(messages => [...messages, msgObject]);
    const response: Message = await sendPrompt(msgObject);
    setMessages(messages => [...messages, response]);
  } 

  return (
    <div className="flex flex-col h-screen justify-center py-10">
      <div className="bg-gray-500 grow max-h-[40rem] rounded-2xl p-5 overflow-y-auto hide-scrollbar">
        {messages.map((messageObj, idx) => {
           return <ChatBubble messageObject={messageObj} key={idx}/>;
        })}
        { loading && <div id="spinner " className="custom-spin border-4 border-t-transparent rounded-[50%] w-8 h-8"/>}
        <div className="h-[10rem]" ref={scrollRef}></div>
      </div>
      <ChatBar addMessage={addMessage}/>
    </div>
  );
}

export function ChatBar ({ addMessage } : { addMessage: (message: string, fromUser: boolean) => void}) {
  const [input, setInput] = useState("")

  function handlePrompt (eventObject: React.FormEvent<HTMLFormElement>) {
    eventObject.preventDefault();

    addMessage(input, true);
    setInput("");
  }

  return (
      <div className="">
          <label htmlFor="user-input" className="sr-only">
              Enter prompt.
          </label>
          <form className="flex flex-row items-center mt-5" onSubmit={handlePrompt}>
              <input onChange={e => setInput(e.target.value)} value={input} name="prompt" placeholder="Ask a question" id="user-input" className="bg-white w-[75rem] rounded-2xl mr-5 text-black p-3" type="text"/>
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
        className={`max-w-[35rem] px-4 py-2 rounded-2xl text-lg
          ${messageObject.fromUser
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-gray-200 text-black rounded-bl-none'
          }`}
      >
        <ReactMarkdown>{messageObject.text}</ReactMarkdown>
      </div>
    </div>
  );
}