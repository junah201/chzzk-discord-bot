import Footer from "./components/footer";
import Header from "./components/header";

export default function MarketingLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
      <Header />
      <main>{children}</main>
      <Footer />
    </div>
  );
}
