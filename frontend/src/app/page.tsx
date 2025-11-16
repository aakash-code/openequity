import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Professional Equity Research,
            <br />
            <span className="text-primary-600">Free and Open Source</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Bridge the $20,000+ annual cost barrier of Bloomberg Terminal. Get institutional-quality research tools with native CFA curriculum integration.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/auth?mode=register"
              className="bg-primary-600 text-white px-8 py-3 rounded-lg hover:bg-primary-700 transition font-medium"
            >
              Get Started Free
            </Link>
            <Link
              href="/auth"
              className="border border-gray-300 px-8 py-3 rounded-lg hover:bg-gray-50 transition font-medium"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Everything You Need for Equity Research
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Financial Analysis
            </h3>
            <p className="text-gray-600">
              Calculate 70+ financial ratios, generate common-size statements, and perform DuPont analysis with ease.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">💹</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Valuation Models
            </h3>
            <p className="text-gray-600">
              Build DCF, comparable company, and precedent transaction models with integrated spreadsheet functionality.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">📈</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Real-time Data
            </h3>
            <p className="text-gray-600">
              Access live quotes, historical prices, and SEC filings all in one platform.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              AI-Powered Analysis
            </h3>
            <p className="text-gray-600">
              Leverage NLP for earnings call analysis, sentiment scoring, and risk extraction from filings.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">🎓</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              CFA Integration
            </h3>
            <p className="text-gray-600">
              Practice tools, mock exams, and features mapped to CFA Learning Outcome Statements.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">👥</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Collaboration
            </h3>
            <p className="text-gray-600">
              Work with teams in real-time, share models, and build together with full version control.
            </p>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-primary-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2">$0</div>
              <div className="text-primary-100">Annual Cost</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">100%</div>
              <div className="text-primary-100">Open Source</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">∞</div>
              <div className="text-primary-100">Customizable</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="bg-gray-900 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">
            Ready to democratize your equity research?
          </h2>
          <p className="text-gray-300 mb-8 text-lg">
            Join thousands of students, investors, and professionals using OpenEquity
          </p>
          <Link
            href="/auth?mode=register"
            className="inline-block bg-primary-600 text-white px-8 py-3 rounded-lg hover:bg-primary-700 transition font-medium"
          >
            Start Free Today
          </Link>
        </div>
      </div>
    </main>
  );
}
