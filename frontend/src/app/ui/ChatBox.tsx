'use client';

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { ChatBar } from "./ChatBar";
import Typewriter from "./TypewriterEffect";

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
      <div className="bg-gray-500 grow max-h-[75vh] rounded-2xl p-5 overflow-y-auto hide-scrollbar">
        {messages.map((messageObj, idx) => {
           return <ChatBubble messageObject={messageObj} key={idx}/>;
        })}
        { loading && <div id="spinner " className="custom-spin border-4 border-t-transparent rounded-[50%] w-8 h-8"/>}
        <div className="h-[10rem]" ref={scrollRef}/>
      </div>
      <ChatBar loadingBoolean={loading} addMessage={addMessage}/>
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
        <Typewriter text={messageObject.text}></Typewriter>
      </div>
    </div>
  );
}


