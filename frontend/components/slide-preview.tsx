"use client";

import type { Slide } from "@/lib/types";
import { motion } from "framer-motion";
import SlideRenderer from "@/components/slides/SlideRenderer";

interface SlidePreviewProps {
  slide: Slide;
  mini?: boolean;
}

export default function SlidePreview({
  slide,
  mini = false,
}: SlidePreviewProps) {
  return <SlideRenderer slide={slide} mini={mini} />;
}