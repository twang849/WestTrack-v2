import { useState } from "react";

export function ChatBar ({ loadingBoolean, addMessage } : { loadingBoolean: boolean, addMessage: (message: string, fromUser: boolean) => void}) {
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
              <input onChange={e => setInput(e.target.value)} inert={loadingBoolean} value={input} name="prompt" placeholder="Ask a question" id="user-input" className="inert:opacity-50 transition bg-white w-[75rem] rounded-2xl mr-5 text-black p-3" type="text"/>
              <button inert={ input == ""} className="bg-black rounded-2xl p-1 hover:bg-gray-700 active:bg-gray-500 inert:opacity-50 transition">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3" />
                  </svg>
              </button>
          </form>
      </div>
  );
}