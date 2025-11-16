# OpenEquity Frontend

Next.js-based frontend for the OpenEquity Research Platform.

## Tech Stack

- **Framework:** Next.js 14+ with App Router
- **Language:** TypeScript 5.0+
- **Styling:** Tailwind CSS 3.0+
- **State Management:** Redux Toolkit
- **Data Fetching:** TanStack Query
- **Charts:** Recharts + D3.js
- **Testing:** Jest + React Testing Library

## Getting Started

### Prerequisites

- Node.js >= 18.17.0
- npm >= 9.0.0

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

### Build

```bash
npm run build
npm start
```

### Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Type Checking

```bash
npm run type-check
```

## Project Structure

```
src/
├── app/              # Next.js app router pages
├── components/       # React components
├── lib/             # Utility functions and configurations
├── hooks/           # Custom React hooks
├── types/           # TypeScript type definitions
└── styles/          # Global styles
```

## Environment Variables

Copy `.env.example` to `.env.local` and configure:

```bash
cp .env.example .env.local
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [OpenEquity Documentation](../docs/)
