import Navbar from "@/components/NavBar";
import ImageSection from "@/components/ImageSection";
import Features from "@/components/Features";
import About from "@/components/About";
import FAQ from "@/components/FAQ";
import Footer from "@/components/Footer";
export default function Home() {
  return (
    <div>
      <Navbar />
      <ImageSection />
      <Features />
      <About/>
      <FAQ/>
      <Footer/>
    </div>
  );
}
