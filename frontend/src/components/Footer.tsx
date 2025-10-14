"use client";
import { Arrow, Github, LinkedIn, X } from "@/Effects/Icons";
import Image from "next/image";
import { useEffect, useState } from "react";
export default function Footer() {
  const [installationUrl, setInstallationUrl] = useState<string>("");

  useEffect(() => {
    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    fetch(`${backendUrl}/api/github-app-info`)
      .then((res) => res.json())
      .then((data) => setInstallationUrl(data.installation_url));
  });
  return (
    <footer className="relative w-full">
      <div className="relative bg-gradient-to-b from-[#073d3d33] to-[#00000033] rounded-[30px] py-1 -mx-4">
        <div className="absolute inset-0 pointer-events-none">
          <div
            className="absolute inset-0 border border-[#0bb6c0] rounded-[30px]"
            style={{
              maskImage:
                "linear-gradient(to bottom, black 0%, black 70%, transparent 100%)",
              WebkitMaskImage:
                "linear-gradient(to bottom, black 0%, black 70%, transparent 100%)",
            }}
          ></div>
        </div>
        <div className="bg-[rgba(29,55,55,0.1)] rounded-[30px] m-4 md:m-6 lg:m-8 px-6 md:px-8 lg:px-12 pt-6 md:pt-8 lg:pt-12 pb-4 md:pb-6 lg:pb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16">
            <div className="flex flex-col justify-between">
              <div className="flex items-center px-4 pb-2 md:pb-0">
                <div className="relative w-40 h-20 md:w-40 lg:h-30 lg:w-60 lg:-translate-y-[40px]">
                  <Image
                    src="/Logo.png"
                    alt="Brainly Logo"
                    fill
                    className="object-contain"
                  />
                </div>
              </div>
              <div className="pl-6">
                <div className="mb-10">
                  <h2 className="text-2xl md:text-3xl lg:text-3xl text-white font-'Montserrat' leading-tight">
                    Ready to Build Smarter?
                  </h2>
                </div>
                <div className="relative">
                  <div className="absolute cursor-pointer rounded-4xl shadow-[inset_0.21887646615505219px_0.3647941052913666px_2.9183528423309326px_0px_rgba(3,78,78,1.00)] outline-8 outline-white/20 ">
                    <a
                      href={installationUrl || "#"}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => {
                        if (!installationUrl) e.preventDefault();
                      }}
                    >
                      <button className="px-6 py-4 cursor-pointer bg-white rounded-4xl shadow-[inset_0px_12px_8px_0px_rgba(174,203,192,1)] flex items-center gap-6  transition-transform">
                        <span className="text-black text-lg font-'Montserrat' font-medium">
                          Start Now
                        </span>
                        <div className="relative">
                          <Arrow />
                        </div>
                      </button>
                    </a>
                  </div>
                </div>
                <div className="pt-24 md:pt-18 lg:translate-y-[30px]">
                  <p className="text-[#999999] text-lg pb-6 md:pb-2">
                    Our Social Handles
                  </p>
                  <div className="flex space-x-3 pb-4 md:pb-0">
                    <a
                      href="#"
                      className="hover:transform hover:scale-110 transition-transform duration-300"
                    >
                      <div className="w-12 h-12 md:w-14 md:h-14 relative">
                        <LinkedIn />
                      </div>
                    </a>
                    <a
                      href="#"
                      className="hover:transform hover:scale-110 transition-transform duration-300"
                    >
                      <div className="w-12 h-12 md:w-14 md:h-14 relative">
                        <Github />
                      </div>
                    </a>
                    <a
                      href="#"
                      className="hover:transform hover:scale-110 transition-transform duration-300"
                    >
                      <div className="w-12 h-12 md:w-14 md:h-14 relative">
                        <X />
                      </div>
                    </a>
                  </div>
                </div>
                <div className="text-[#999999] text-md lg:translate-y-[60px]">
                  <span>@2025 </span>
                  <span className="text-white">All Rights Reserved</span>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12 pl-6 md:pl-0">
              <div className="space-y-8">
                <h3 className="text-white text-2xl md:text-3xl font-'Montserrat' font-medium">
                  Quick Links
                </h3>
                <ul className="space-y-8 text-[#999999] text-lg md:text-xl">
                  <li>
                    <a
                      href="#"
                      className="hover:text-white transition-colors duration-300"
                    >
                      Home
                    </a>
                  </li>
                  <li>
                    <a
                      href="#"
                      className="hover:text-white transition-colors duration-300"
                    >
                      Features
                    </a>
                  </li>
                  <li>
                    <a
                      href="#"
                      className="hover:text-white transition-colors duration-300"
                    >
                      How It Works
                    </a>
                  </li>
                  <li>
                    <a
                      href="#"
                      className="hover:text-white transition-colors duration-300"
                    >
                      FAQ
                    </a>
                  </li>
                  <li>
                    <a
                      href="#"
                      className="hover:text-white transition-colors duration-300"
                    >
                      Contact
                    </a>
                  </li>
                </ul>
              </div>
              <div>
                <div className="pb-8 md:pb-15 ">
                  <h3 className="text-white text-2xl md:text-3xl font-'Montserrat' font-medium">
                    Contact
                  </h3>
                  <div className="text-[#999999] pt-8 text-lg md:text-xl">
                    <p>
                      <span>Email: Krish</span>
                      <a
                        href="mailto:support@yourdomain.com"
                        className="text-[#999999] hover:text-white transition-colors duration-300"
                      >
                        @gmail.com
                      </a>
                    </p>
                  </div>
                </div>
                <div>
                  <h3 className="text-white text-2xl pb-9 md:text-3xl font-'Montserrat' lg:pb-8 font-medium">
                    Legal
                  </h3>
                  <ul className="space-y-8 text-[#999999] text-lg md:text-xl">
                    <li>
                      <a
                        href="#"
                        className="hover:text-white transition-colors duration-300"
                      >
                        Privacy Policy
                      </a>
                    </li>
                    <li>
                      <a
                        href="#"
                        className="hover:text-white transition-colors duration-300"
                      >
                        Terms of Service
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
