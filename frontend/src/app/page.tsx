import Image from "next/image";
import Background from "./ui/Background";
import ChatWindow from "./ui/ChatWindow";

export default function Home() {
  return (
    <>
      <Background>
        <ChatWindow/>
      </Background>
    </>
  );
}
