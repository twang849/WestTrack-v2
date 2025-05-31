
export default function ChatWindow () {

    return (
        <div className="flex flex-col justify-end bg-gray-600 h-5/6 w-3/6">
            <div className="flex flex-row items-center">
                <input id="user-input" className="bg-white rounded-2xl m-5 w-[85%] text-black p-2" type="text"/>
                <div className="bg-black rounded-2xl p-1">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3" />
                    </svg>
                </div>
            </div>
        </div>
    );
}