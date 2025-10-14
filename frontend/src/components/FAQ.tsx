"use client";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";

export default function FAQ() {
  const [openItems, setOpenItems] = useState<Set<number>>(new Set());

  const toggleItem = (index: number) => {
    const newOpenItems = new Set(openItems);
    if (newOpenItems.has(index)) {
      newOpenItems.delete(index);
    } else {
      newOpenItems.add(index);
    }
    setOpenItems(newOpenItems);
  };

  const faqData = [
    {
      question: "How does automated PR review work?",
      answer:
        "When you open a pull request, our AI automatically analyzes your code changes within minutes. It creates a knowledge graph of your codebase, runs 40+ linters, maps dependencies, and generates line-by-line feedback with security findings and improvement suggestions—all without manual triggers.",
    },
    {
      question: "Is my code safe and private?",
      answer:
        "Your code is processed securely and shared only with trusted AI providers for review purposes. We never use your code to train any AI models.",
    },
    {
      question: "What programming languages and frameworks are supported?",
      answer:
        "We support a wide range of programming languages including JavaScript, TypeScript, Python, C, Rust and many more later on. Our AI is continuously updated to support new technologies.",
    },
    {
      question: "How does this fit into my existing development workflow?",
      answer:
        "Install our GitHub app in minutes and reviews start automatically on every PR. Interact with the AI directly in PR comments, get AI-generated summaries",
    },
  ];

  return (
    <div className="relative w-full min-h-screen bg-black py-8 sm:py-12 lg:py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="relative mb-8 sm:mb-12 lg:mb-16 max-w-full">
          <div className="relative mb-6 sm:mb-8">
            <div className="bg-gradient-to-b from-[#068e8e] from-10% to-90% to-[#083440]/25 rounded-full sm:rounded-[20px] lg:rounded-[26px] w-fit px-4 sm:px-6 lg:px-10 py-2 sm:py-3 lg:py-4">
              <p className="text-white text-2xl md:text-4xl font-normal font-'Montserrat'">
                FAQs
              </p>
            </div>
          </div>
          <div className="relative">
            <div className="text-white text-3xl sm:text-4xl md:text-5xl lg:text-5xl font-normal font-'Montserrat' mb-2 sm:mb-4">
              Need Help?
            </div>
            <div className="bg-clip-text text-transparent bg-gradient-to-r from-[#006F91] from-5% to-20% to-[#0BB6C0]  text-3xl sm:text-4xl md:text-5xl lg:text-5xl font-normal font-'Montserrat'">
              Start Here
            </div>
          </div>
        </div>
        <div className="space-y-4 sm:space-y-6 max-w-full">
          {faqData.map((faq, index) => (
            <motion.div
              key={index}
              className="relative w-full cursor-pointer"
              onClick={() => toggleItem(index)}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              transition={{ duration: 0.2 }}
            >
              <div className="absolute inset-0 bg-gradient-to-b from-[#056f6f66] to-[#0834401a] rounded-4xl border-6 border-[#022324]" />
              <div className="relative px-4 sm:px-8 md:px-12 lg:px-16 xl:px-24 py-6 sm:py-8 lg:py-8">
                <div className="flex items-center justify-between">
                  <p className="text-white text-md sm:text-2xl lg:text-3xl font-normal font-'Montserrat' sm:leading-none pr-4">
                    {faq.question}
                  </p>
                  <motion.div
                    animate={{ rotate: openItems.has(index) ? 45 : 0 }}
                    transition={{ duration: 0.3 }}
                    className="text-white text-2xl sm:text-3xl lg:text-4xl font-light"
                  >
                    +
                  </motion.div>
                </div>
                <AnimatePresence>
                  {openItems.has(index) && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.4, ease: "easeInOut" }}
                      className="overflow-hidden"
                    >
                      <motion.div
                        initial={{ y: -20 }}
                        animate={{ y: 0 }}
                        exit={{ y: -20 }}
                        transition={{ duration: 0.3, delay: 0.1 }}
                        className="pt-4 sm:pt-6 lg:pt-8"
                      >
                        <div className="w-full h-px bg-gradient-to-r from-transparent via-[#056f6f] to-transparent mb-4 sm:mb-6 lg:mb-8" />
                        <p className="text-gray-300 text-sm sm:text-lg lg:text-2xl font-normal font-'Montserrat' leading-relaxed">
                          {faq.answer}
                        </p>
                      </motion.div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
