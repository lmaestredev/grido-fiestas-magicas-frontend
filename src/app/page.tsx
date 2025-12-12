import HeroSection from "~/components/HeroSection";
import FormSection from "~/components/FormSection";
import PromoBanner from "~/components/PromoBanner";
import Footer from "~/components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <HeroSection />
      <FormSection />
      <PromoBanner />
      <Footer />
    </main>
  );
}
