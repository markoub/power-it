"use client";

import { useEffect, useRef, useState } from 'react';

interface SimpleAvatarProps {
  text: string;
  isPlaying: boolean;
  onPlay?: () => void;
  onStop?: () => void;
  onEnded?: () => void;
}

export function SimpleAvatar({ text, isPlaying, onPlay, onStop, onEnded }: SimpleAvatarProps) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [mouthOpen, setMouthOpen] = useState(0); // 0 = closed, 1 = slightly open, 2 = open, 3 = wide
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const animationRef = useRef<NodeJS.Timeout | null>(null);

  // Animate mouth while speaking
  useEffect(() => {
    if (isSpeaking) {
      const animateMouth = () => {
        setMouthOpen(prev => (prev + 1) % 4);
      };
      
      // Change mouth shape every 150ms
      animationRef.current = setInterval(animateMouth, 150);
    } else {
      // Clear animation and close mouth
      if (animationRef.current) {
        clearInterval(animationRef.current);
        animationRef.current = null;
      }
      setMouthOpen(0);
    }

    return () => {
      if (animationRef.current) {
        clearInterval(animationRef.current);
      }
    };
  }, [isSpeaking]);

  useEffect(() => {
    if (!text || !('speechSynthesis' in window)) return;

    const handleSpeech = () => {
      if (isPlaying) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utteranceRef.current = utterance;
        
        // Configure voice
        utterance.rate = 0.9;
        utterance.pitch = 1.1;
        utterance.volume = 1.0;
        
        // Select a female voice if available
        const voices = window.speechSynthesis.getVoices();
        const femaleVoice = voices.find(voice => 
          voice.name.includes('Female') || 
          voice.name.includes('Samantha') ||
          voice.name.includes('Victoria') ||
          voice.name.includes('Karen')
        );
        if (femaleVoice) {
          utterance.voice = femaleVoice;
        }
        
        utterance.onstart = () => {
          setIsSpeaking(true);
          onPlay?.();
        };
        
        utterance.onend = () => {
          setIsSpeaking(false);
          onStop?.();
          onEnded?.();
        };
        
        utterance.onerror = () => {
          setIsSpeaking(false);
          onStop?.();
        };
        
        window.speechSynthesis.speak(utterance);
      } else {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
        onStop?.();
      }
    };

    handleSpeech();

    return () => {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    };
  }, [isPlaying, text, onPlay, onStop, onEnded]);

  // Get mouth shape based on current state
  const getMouthShape = () => {
    switch (mouthOpen) {
      case 0: // Closed
        return <path d="M 40 60 Q 50 58 60 60" stroke="#8b4513" strokeWidth="3" fill="none" />;
      case 1: // Slightly open
        return <ellipse cx="50" cy="60" rx="8" ry="3" fill="none" stroke="#8b4513" strokeWidth="3" />;
      case 2: // Open
        return <ellipse cx="50" cy="60" rx="10" ry="6" fill="#d2691e" stroke="#8b4513" strokeWidth="3" />;
      case 3: // Wide open
        return <ellipse cx="50" cy="60" rx="12" ry="8" fill="#d2691e" stroke="#8b4513" strokeWidth="3" />;
      default:
        return <path d="M 40 60 Q 50 58 60 60" stroke="#8b4513" strokeWidth="3" fill="none" />;
    }
  };

  // Simple SVG avatar
  return (
    <div className="relative w-full h-full bg-gradient-to-b from-blue-100 to-blue-200 rounded-lg overflow-hidden flex items-center justify-center">
      <svg
        width="200"
        height="200"
        viewBox="0 0 100 100"
        className={`transition-transform ${isSpeaking ? 'scale-105' : 'scale-100'}`}
      >
        {/* Head */}
        <circle cx="50" cy="50" r="35" fill="#fdbcb4" stroke="#e8a39b" strokeWidth="2" />
        
        {/* Eyes */}
        <circle cx="35" cy="45" r="3" fill="#333">
          {isSpeaking && (
            <animate attributeName="r" values="3;2;3" dur="2s" repeatCount="indefinite" />
          )}
        </circle>
        <circle cx="65" cy="45" r="3" fill="#333">
          {isSpeaking && (
            <animate attributeName="r" values="3;2;3" dur="2s" repeatCount="indefinite" />
          )}
        </circle>
        
        {/* Eyebrows */}
        <path d="M 30 40 Q 35 38 40 40" stroke="#8b4513" strokeWidth="2" fill="none" />
        <path d="M 60 40 Q 65 38 70 40" stroke="#8b4513" strokeWidth="2" fill="none" />
        
        {/* Nose */}
        <path d="M 50 50 L 48 55 L 52 55 Z" fill="#e8a39b" />
        
        {/* Mouth - Animated based on state */}
        <g className="transition-all duration-100">
          {getMouthShape()}
        </g>
        
        {/* Hair */}
        <path
          d="M 20 35 Q 50 20 80 35 Q 85 50 80 45 Q 75 30 70 32 Q 65 25 60 28 Q 50 22 40 28 Q 35 25 30 32 Q 25 30 20 45 Q 15 50 20 35"
          fill="#8b4513"
        />
      </svg>
      
      {/* Speaking indicator */}
      {isSpeaking && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-1">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      )}
      
      {/* Text display */}
      <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white p-2 text-sm text-center">
        {isSpeaking ? 'Speaking...' : 'Ready to speak'}
      </div>
    </div>
  );
}