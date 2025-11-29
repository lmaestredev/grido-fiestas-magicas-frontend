import Image from "next/image";

export default function Footer() {
  return (
    <footer className="bg-grido-primary w-full">
      <div className="max-w-7xl mx-auto px-6 lg:px-[141px] py-[55px]">
        <div className="flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Logo */}
          <div className="shrink-0">
            <Image
              src="/images/grido-logo.png"
              alt="Grido"
              width={100}
              height={71}
              quality={100}
              className="object-contain"
            />
          </div>

          {/* Text */}
          <p className="text-white text-center md:text-left max-w-[500px]">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
          </p>

          {/* Social Links */}
          <a
            href="https://www.instagram.com/gridohelados/"
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 hover:opacity-80 transition-opacity"
            aria-label="Seguinos en Instagram"
          >
            <Image
              src="/images/instagram-icon.png"
              alt="Instagram"
              width={26}
              height={26}
              quality={100}
              className="object-contain invert brightness-0 filter"
            />
          </a>
        </div>
      </div>
    </footer>
  );
}
