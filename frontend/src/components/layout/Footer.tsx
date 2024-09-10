import React from 'react'

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-800 text-white">
      <div className="container mx-auto px-4 py-6 text-center">
        <p>&copy; {new Date().getFullYear()} LLM Code Navigator. All rights reserved.</p>
      </div>
    </footer>
  )
}

export default Footer