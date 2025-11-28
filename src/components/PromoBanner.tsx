import Image from "next/image";

// Banner image dimensions from Figma: 1280x636
const BANNER_WIDTH = 1280;
const BANNER_HEIGHT = 636;

export default function PromoBanner() {
  return (
    <section className="relative w-full overflow-hidden">
      {/* Container that maintains aspect ratio */}
      <div 
        className="relative w-full"
        style={{ aspectRatio: `${BANNER_WIDTH}/${BANNER_HEIGHT}` }}
      >
        {/* Image scaled slightly to hide 1px transparent border at bottom */}
        <Image
          src="/images/footer-banner.png"
          alt="Noche Mágica - Traé tu cartita a Papá Noel y llevate 1 helado de regalo. Te esperamos el 18/12, 18hs."
          fill
          className="object-contain object-center scale-[1.002] translate-y-px"
          quality={100}
          sizes="100vw"
        />
      </div>
    </section>
  );
}
