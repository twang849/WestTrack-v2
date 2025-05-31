import Image from "next/image";
import Background from "./ui/Background";
import ChatBar from "./ui/ChatBar";

export default function Home() {
  return (
    <>
      <Background>
        <div className="bg-gray-500 h-auto w-[50rem]"></div>
        <ChatBar/>
      </Background>
    </>
  );
}
