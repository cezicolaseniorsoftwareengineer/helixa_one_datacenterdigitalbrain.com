'use client';

import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { 
  OrbitControls, 
  PerspectiveCamera, 
  Float, 
  MeshDistortMaterial, 
  Sphere, 
  ContactShadows, 
  Environment,
  RoundedBox,
  Text
} from '@react-three/drei';
import * as THREE from 'three';

function ServerRack({ position, color, label }: { position: [number, number, number], color: string, label: string }) {
  return (
    <group position={position}>
      {/* Main Frame */}
      <RoundedBox args={[1, 2, 1]} radius={0.05} smoothness={4}>
        <meshStandardMaterial color="#1a1a1a" metalness={0.8} roughness={0.2} />
      </RoundedBox>
      
      {/* Front Glass/Panel */}
      <mesh position={[0, 0, 0.51]}>
        <planeGeometry args={[0.8, 1.8]} />
        <meshStandardMaterial 
          color={color} 
          emissive={color} 
          emissiveIntensity={0.5} 
          transparent 
          opacity={0.6} 
        />
      </mesh>

      {/* Internal "Servers" (Visual Detail) */}
      {[...Array(8)].map((_, i) => (
        <mesh key={i} position={[0, 0.7 - i * 0.2, 0.45]}>
          <boxGeometry args={[0.7, 0.1, 0.1]} />
          <meshStandardMaterial color="#333" />
        </mesh>
      ))}

      <Text
        position={[0, 1.2, 0]}
        fontSize={0.15}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {label}
      </Text>
    </group>
  );
}

function Laptop({ position, color, label }: { position: [number, number, number], color: string, label: string }) {
  return (
    <group position={position}>
      {/* Base */}
      <RoundedBox args={[1.2, 0.05, 0.8]} position={[0, 0, 0]} radius={0.02}>
        <meshStandardMaterial color="#222" metalness={0.9} roughness={0.1} />
      </RoundedBox>
      {/* Screen */}
      <group position={[0, 0.02, -0.4]} rotation={[-Math.PI / 4, 0, 0]}>
        <RoundedBox args={[1.2, 0.8, 0.05]} position={[0, 0.4, 0]} radius={0.02}>
          <meshStandardMaterial color="#111" />
        </RoundedBox>
        <mesh position={[0, 0.4, 0.03]}>
          <planeGeometry args={[1.1, 0.7]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.4} />
        </mesh>
      </group>
    </group>
  );
}

function DesktopPC({ position, color, label }: { position: [number, number, number], color: string, label: string }) {
  return (
    <group position={position}>
      {/* Case */}
      <RoundedBox args={[0.5, 1.2, 1]} radius={0.05}>
        <meshStandardMaterial color="#111" metalness={0.7} roughness={0.3} />
      </RoundedBox>
      {/* Side Panel (RGB/Status) */}
      <mesh position={[0.26, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
        <planeGeometry args={[0.9, 1.1]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} transparent opacity={0.5} />
      </mesh>
    </group>
  );
}

function DataCenterScene({ temp, mode }: { temp: number, mode: 'pc' | 'notebook' | 'datacenter' }) {
  const statusColor = useMemo(() => {
    if (temp > 30) return '#ef4444';
    if (temp > 25) return '#eab308';
    return '#22c55e';
  }, [temp]);

  return (
    <>
      <Environment preset="city" />
      <ambientLight intensity={0.2} />
      <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={2} castShadow />

      {/* Asset Grid based on Mode */}
      <group position={[0, 0, 0]}>
        {mode === 'notebook' && (
          <Laptop position={[0, 0, 0]} color={statusColor} label="LOCAL-NOTEBOOK" />
        )}
        
        {mode === 'pc' && (
          <DesktopPC position={[0, 0.5, 0]} color={statusColor} label="LOCAL-WORKSTATION" />
        )}

        {mode === 'datacenter' && (
          <group>
            <ServerRack position={[-1.5, 1, 0]} color={statusColor} label="RACK-01" />
            <ServerRack position={[0, 1, 0]} color={statusColor} label="RACK-02" />
            <ServerRack position={[1.5, 1, 0]} color={statusColor} label="RACK-03" />
          </group>
        )}
      </group>

      {/* Central Core (AI Brain) */}
      <Float speed={temp > 28 ? 10 : 3} rotationIntensity={temp > 28 ? 5 : 2} floatIntensity={temp > 28 ? 5 : 2}>
        <Sphere args={[0.4, 64, 64]} position={[0, 3, -1]}>
          <MeshDistortMaterial
            color={temp > 28 ? "#ff003c" : "#06b6d4"}
            speed={temp > 28 ? 10 : 4}
            distort={temp > 28 ? 0.8 : 0.5}
            radius={1}
            emissive={temp > 28 ? "#ff003c" : "#06b6d4"}
            emissiveIntensity={temp > 28 ? 1 : 0.5}
          />
        </Sphere>
      </Float>

      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]} receiveShadow>
        <planeGeometry args={[50, 50]} />
        <meshStandardMaterial color="#050505" roughness={0.1} metalness={0.2} />
      </mesh>

      <ContactShadows position={[0, 0, 0]} opacity={0.4} scale={20} blur={2} far={4.5} />
      <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 1.75} />
    </>
  );
}

export default function DigitalTwin({ temp, mode = 'datacenter' }: { temp: number, mode?: 'pc' | 'notebook' | 'datacenter' }) {
  return (
    <div className="w-full h-full bg-gradient-to-b from-black to-[#050505] rounded-xl overflow-hidden border border-white/5">
      <Canvas shadows dpr={[1, 2]}>
        <PerspectiveCamera makeDefault position={[0, 5, 10]} fov={45} />
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <spotLight position={[-10, 10, 10]} angle={0.15} penumbra={1} intensity={1} />
        <DataCenterScene temp={temp} mode={mode} />
        <Environment preset="city" />
      </Canvas>
    </div>
  );
}

