import Image from "next/image";
import { LineEffect } from "../Effects/Design";
import {
  TopStarEffect,
  BottomStarEffect,
} from "../Effects/BackgroundGradients";
export default function About() {
  return (
    <div
      className="relative w-full min-h-screen bg-black/5 p-4 sm:p-8 lg:p-16"
      data-name="About"
    >
      <div className="absolute lg:inset-16 rounded-3xl" />
      <div
        className="absolute left-1/2 z-20 top-[280px] sm:top-[320px] hidden lg:block lg:top-[25%] lg:left-[31%] w-[600px] sm:w-[800px] lg:w-[800px] lg:scale-100 transform -translate-x-1/2"
        data-name="Line Effect"
      >
        <div className="absolute">
          <LineEffect />
        </div>
      </div>
      <div className="relative z-10 max-w-7xl mx-auto py-8 sm:py-12 lg:py-16">
        <div className="text-center mb-12 sm:mb-16 lg:mb-28">
          <div className="lg:mb-10">
            <h2 className="text-2xl sm:text-4xl lg:text-6xl  font-normal font-'Montserrat' mb-4 sm:mb-6">
              <span className="bg-clip-text bg-gradient-to-r from-white from-40% to-gray-500 to-70% text-transparent">
                How It Works: From{" "}
              </span>
            </h2>
          </div>
          <div className="flex items-center justify-center gap-2 sm:gap-4">
            <span className="text-2xl sm:text-4xl lg:text-6xl  font-normal font-'Montserrat' bg-clip-text bg-white leading-relaxed">
              Upload To
            </span>
            <div className="px-2 lg:px-2">
              <div className="max-w-[25px] md:max-w-[40px] lg:max-w-[60px]">
                <Image src="/Eye.png" alt="Eye" width={60} height={30} />
              </div>
            </div>
            <span className="text-2xl sm:text-4xl lg:text-6xl font-normal font-'Montserrat' bg-clip-text bg-gray-500 text-transparent leading-relaxed">
              Insight
            </span>
          </div>
        </div>
        <div className="relative">
          <div className="absolute hidden lg:block top-0 left-1/2 transform -translate-x-1/2 -translate-y-[190px] z-0">
            <TopStarEffect />
          </div>
          <div className="absolute hidden lg:block bottom-0 right-1/2 transform translate-x-1/2 translate-y-[190px] z-0">
            <BottomStarEffect />
          </div>
          <div className="absolute inset-0 bg-black/70 rounded-3xl z-1 -my-4" />
          <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-x-6 gap-y-12 sm:gap-x-8 sm:gap-y-16 lg:gap-x-30 lg:gap-y-40 max-w-5xl mx-auto">
            <div className="relative group">
              <div className="bg-gradient-to-b from-[#1587a666] from-1% to-[#083440]/25 to-10% rounded-3xl p-6 sm:p-8 h-auto min-h-[400px] sm:min-h-[450px] lg:min-h-[500px] flex flex-col">
                <div className="flex mb-10">
                  <div className="w-[200px] sm:w-[250px] bg-center bg-cover bg-no-repeat rounded-lg">
                    <Image
                      src="/Codebase.png"
                      alt="Codebase"
                      width={300}
                      height={100}
                    />
                  </div>
                </div>
                <div className="text-left">
                  <h3 className="text-xl sm:text-2xl lg:text-3xl font-medium font-'Montserrat' mb-4 sm:mb-8 bg-clip-text text-transparent bg-gradient-to-r from-white from-40% to-gray-500 to-70%">
                    Upload Your Codebase
                  </h3>
                  <p className="text-white font-light font-'Montserrat' text-base sm:text-lg lg:text-xl leading-relaxed">
                    Drag and drop your entire project folder or connect your
                    repository in seconds. Our smart indexing ensures every
                    file, dependency, and relationship is mapped for instant
                    understanding.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative group">
              <div className="bg-gradient-to-b from-[#1587a666] from-1% to-[#083440]/25 to-10% rounded-3xl p-6 sm:p-8 h-auto min-h-[400px] sm:min-h-[450px] lg:min-h-[500px] flex flex-col">
                <div className="flex mb-5">
                  <div className="w-[200px] sm:w-[170px] bg-center bg-cover bg-no-repeat rounded-lg">
                    <Image
                      src="/Structure.png"
                      alt="Structure"
                      width={300}
                      height={100}
                    />
                  </div>
                </div>
                <div className="text-left">
                  <h3 className="text-xl sm:text-2xl lg:text-3xl font-medium font-'Montserrat' mb-4 sm:mb-7 bg-clip-text text-transparent bg-gradient-to-r from-white from-40% to-gray-500 to-70%">
                    Ask Anything, Anytime
                  </h3>
                  <p className="text-white font-light font-'Montserrat' text-base sm:text-lg lg:text-xl leading-relaxed">
                    Interact naturally with your AI assistant. Whether you need
                    help implementing a feature, understanding code, or
                    debugging, just ask—no need to reference specific files or
                    lines.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative group">
              <div className="bg-gradient-to-b from-[#1587a666] from-1% to-[#083440]/25 to-10% rounded-3xl p-6 sm:p-8 h-auto min-h-[400px] sm:min-h-[450px] lg:min-h-[500px] flex flex-col">
                <div className="flex mb-8">
                  <div className="w-[200px] sm:w-[170px] bg-center bg-cover bg-no-repeat rounded-lg">
                    <Image
                      src="/Context.png"
                      alt="Context"
                      width={300}
                      height={100}
                    />
                  </div>
                </div>
                <div className="text-left">
                  <h3 className="text-xl sm:text-2xl lg:text-3xl font-medium font-'Montserrat' mb-4 sm:mb-8 bg-clip-text text-transparent bg-gradient-to-r from-white from-40% to-gray-500 to-70%">
                    Contextual Answers
                  </h3>
                  <p className="text-white font-light font-'Montserrat' text-base sm:text-lg lg:text-xl leading-relaxed">
                    Receive detailed answers, code suggestions, and explanations
                    that consider your entire codebase. AI understands
                    cross-file relationships and dependencies for truly holistic
                    support.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative group">
              <div className="bg-gradient-to-b from-[#1587a666] from-1% to-[#083440]/25 to-10% rounded-3xl p-6 sm:p-8 h-auto min-h-[400px] sm:min-h-[450px] lg:min-h-[500px] flex flex-col">
                <div className="flex mb-12">
                  <div className="w-[200px] sm:w-[180px] bg-center bg-cover bg-no-repeat rounded-lg">
                    <Image
                      src="/Iterate.png"
                      alt="Iterate"
                      width={300}
                      height={100}
                    />
                  </div>
                </div>
                <div className="text-left">
                  <h3 className="text-xl sm:text-2xl lg:text-3xl font-medium font-'Montserrat' mb-4 sm:mb-7 bg-clip-text text-transparent bg-gradient-to-r from-white from-40% to-gray-500 to-70%">
                    Iterate and Collaborate
                  </h3>
                  <p className="text-white font-light font-'Montserrat' text-base sm:text-lg lg:text-xl leading-relaxed">
                    Refine your queries, explore alternative solutions, and
                    collaborate with the AI to accelerate your workflow. Get
                    instant feedback and iterate until you&apos;re satisfied.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
