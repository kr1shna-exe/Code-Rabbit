"use client";

import { Arrow, Rocket, Star } from "@/Effects/Icons";
import { useEffect, useState } from "react";
import { BackgroundGradients } from "../Effects/BackgroundGradients";
import Text from "../Effects/Text";

export default function Navbar() {
  const [installationUrl, setInstallationUrl] = useState<string>("");

  useEffect(() => {
    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    fetch(`${backendUrl}/api/github-app-info`)
      .then((res) => res.json())
      .then((data) => {
        setInstallationUrl(data.installation_url);
      })
      .catch((err) => console.error("Failed to fetch GitHub App info:", err));
  }, []);
  return (
    <div className="relative w-full min-h-screen overflow-hidden">
      <BackgroundGradients />
      <div className="relative z-10 pt-36 flex flex-col items-center justify-center min-h-screen px-4">
        <div className="-translate-y-30">
          <div className="relative px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm">
            <div className="flex items-center gap-2">
              <Text />
            </div>
          </div>
        </div>
        <div className="text-center mb-10">
          <h1 className="text-3xl md:text-6xl font-Montserrat font-normal ">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#ffffff] from-50% to-[#999999] to-75%">
              Transform How You
            </span>
          </h1>
          <div className="flex items-center justify-center gap-4 mt-4">
            <span className="text-3xl md:text-6xl font-Montserrat font-normal bg-clip-text text-transparent bg-[#999999]">
              Build
            </span>
            <Rocket />
            <span className="text-3xl md:text-6xl font-Montserrat font-normal text-[#ffffff]">
              Software
            </span>
          </div>
        </div>
        <p className="text-white text-lg text-center max-w-2xl mb-12 font-Montserrat">
          Seamlessly explore, debug, and Empower your development
          <br />
          with AI that understands your entire project.
        </p>
        <div className="relative mt-20 flex items-center justify-center w-full max-w-4xl">
          <div className="absolute -left-14 md:left-0 top-1/2 w-[30%] h-px bg-gradient-to-r from-transparent to-white/100" />
          <div className="rounded-3xl shadow-[inset_0.21887646615505219px_0.3647941052913666px_2.9183528423309326px_0px_rgba(3,78,78,1.00)] outline-8 outline-white/20 ">
            <a
              href={installationUrl || "#"}
              target="_blank"
              rel="noopener noreferrer"
              className={!installationUrl ? "pointer-events-none" : ""}
            >
              <button className="px-3 py-4 bg-white cursor-pointer rounded-3xl shadow-[inset_0px_12px_8px_0px_rgba(174,203,192,1)] flex items-center hover:scale-105 transition-all duration-300 gap-6">
                <div className="relative">
                  <Star />
                </div>
                <span className="text-black text-lg font-Montserrat font-medium">
                  Start Now
                </span>
                <div className="relative">
                  <Arrow />
                </div>
              </button>
            </a>
          </div>
          <div className="absolute -right-14 md:right-0 top-1/2 w-[30%] h-px bg-gradient-to-l from-transparent to-white/100" />
        </div>
      </div>
      <div className="absolute bottom-0 left-0 w-full h-auto flex justify-center z-0">
        <div className=" backdrop-filter box-border flex flex-row gap-[40px] items-end justify-center p-0">
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#996464]/4 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#996464]/4 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#996464]/4 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#996464]/4 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#999999]/2 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#999999]/6 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#999999]/2 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#996464]/4 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#996464]/4 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#996464]/4 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
          <div className="w-18 h-[1000px] bg-gradient-to-b from-[#996464]/4 from-20% to-black/1 to-100% backdrop-blur-[65px]" />
        </div>
      </div>
    </div>
  );
}
