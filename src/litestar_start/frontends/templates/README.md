# {{ project_name }} Frontend

{{ description }}

## Development Setup

### Prerequisites

- [Node.js](https://nodejs.org/) v20 or higher
- npm (comes with Node.js)

### Installation

```bash
# Install dependencies
cd frontend
npm install
```

### Running the Application

```bash
# Development mode with hot reload
npm run dev
```

The application will be available at `http://localhost:5173`

### Building for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

### Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check (if TypeScript)
npm run type-check
```

### Adding Dependencies

```bash
# Add a production dependency
npm install axios

# Add a dev dependency
npm install --save-dev @types/node

# Update dependencies
npm update
```

### Docker

```bash
# Build image
docker build -t {{ project_slug }}-frontend .

# Run container
docker run -p 80:80 {{ project_slug }}-frontend
```

## Project Structure

```
frontend/
├── src/
│   ├── main.jsx         # Application entry point
│   ├── App.jsx          # Root component
│   ├── components/      # Reusable components
│   ├── pages/           # Page components
│   ├── utils/           # Utility functions
│   └── ...
├── public/              # Static assets
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
├── Dockerfile
└── README.md
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE={{ project_name }}
```

Access in code with `import.meta.env.VITE_API_URL`
