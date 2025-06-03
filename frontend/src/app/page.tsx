import ChatBox from "./ui/ChatComponents";

import { Merriweather } from "next/font/google";

const merriweather = Merriweather({subsets: ['latin'], weight: ['900']})

export default async function Home() {;


  return (
    <div className="bg-purple-800 w-screen h-screen flex flex-col items-center justify-end">
      <div className={`${merriweather.className} text-amber-500 text-3xl mt-8 -mb-2`}>
        WestTrack v2.0
      </div>
      <ChatBox/>
    </div>
  );
}
