export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-soothing flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
            ManoVeil
          </h1>
          <p className="text-gray-500 mt-2 text-sm">Unveiling the Mind</p>
        </div>
        {children}
      </div>
    </div>
  );
}
