import FileGraph from '../FileGraph/FileGraph'
import Footer from './Footer'
import Header from './Header'

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow flex flex-col">
        <div className="flex-grow">
          <FileGraph />
        </div>
        {children}
      </main>
      <Footer />
    </div>
  )
}