export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-6xl font-bold mb-4">
          OpenEquity Research Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Professional-grade equity research tools, democratized.
        </p>
        <div className="flex gap-4 justify-center">
          <button className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition">
            Get Started
          </button>
          <button className="border border-gray-300 px-6 py-3 rounded-lg hover:bg-gray-50 transition">
            View Documentation
          </button>
        </div>
      </div>
    </main>
  )
}
