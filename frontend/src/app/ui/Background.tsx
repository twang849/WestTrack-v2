export default function Background ({ children } : {children: any}) {
    return (
        <div className="flex justify-center items-center bg-purple-700 w-screen h-screen">
            {children}
        </div>
    );
}