export default function Background ({ children } : {children: any}) {
    return (
        <div className="grid grid-rows-[auto_5rem] justify-center pb-5 bg-purple-800 w-screen h-screen">
            {children}
        </div>
    );
}