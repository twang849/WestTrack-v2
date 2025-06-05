import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";


const useTypewriter = (text: string, speed: number) => {
  const [displayText, setDisplayText] = useState('');
  const [index, setIndex] = useState(0);

  useEffect(() => {
      if (index < text.length) {
        const timeout = setTimeout(() => {
            setDisplayText(prevText => prevText + text.charAt(index));
            setIndex(index => index + 1);
        }, speed);
        return () => clearTimeout(timeout);
      }
  }, [index, text, speed]);

  return {displayText, isTyping: index < text.length}
};

export default function Typewriter ({ text, speed=50 } : {text: string, speed?: number}) {
  const {displayText, isTyping } = useTypewriter(text, speed);

  return (
    <div className="inline-flex">
      <ReactMarkdown>{displayText + (isTyping ? "|" : "")}</ReactMarkdown>
      {/* {isTyping && <span className="font-bold">|</span>} */}
    </div>
  );
};