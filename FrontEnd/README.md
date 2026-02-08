# MediQuest Frontend

A modern, responsive healthcare management interface built for patients and medical professionals.

## Features

- **Physician Dashboard**: Monitor patient vitals, active alerts, and recent activity at a glance.
- **Patient Management**: Securely register and manage patient records.
- **Vitals Tracking**: Visual representation of health metrics.
- **Responsive Design**: Optimized for desktop and mobile devices.

## Technology Stack

- **Framework**: [React 19](https://react.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)

## Getting Started

### Prerequisites

- Node.js (v18 or higher recommended)
- npm or yarn

### Installation

1. Clone the repository
2. Navigate to the project directory:
   ```bash
   cd FrontEnd
   ```
3. Install dependencies:
   ```bash
   ```

### Default Credentials (Development)

If the backend database is seeded with default data:

- **Doctor**: `dr_smith` / `Doctor@123`
- **Admin**: `admin` / `Admin@123`
- **Patient**: `john.doe0` / `Patient@123` (if using realistic seeder)

### Development

Start the development server:
```bash
npm run dev
```

### Build

Create a production build:
```bash
npm run build
```
The output will be in the `dist` directory.

## Project Structure

```
FrontEnd/
├── src/
│   ├── components/   # Reusable UI components
│   ├── context/      # React Context (Auth, etc.)
│   ├── pages/        # Application pages
│   ├── services/     # API integration
│   ├── types/        # TypeScript definitions
│   └── index.css     # Global styles & Tailwind
├── public/           # Static assets
└── ...config files   # Vite, Tailwind, TypeScript configs
```
