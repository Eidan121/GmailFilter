import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

const PARTICLE_COUNT = 3000
const RADIUS = 4
const CONNECTION_DIST = 0.6

export function ParticleMesh() {
  const pointsRef = useRef<THREE.Points>(null)
  const linesRef = useRef<THREE.LineSegments>(null)

  const { positions, colors, linePositions } = useMemo(() => {
    const positions = new Float32Array(PARTICLE_COUNT * 3)
    const colors = new Float32Array(PARTICLE_COUNT * 3)

    // Distribute particles on sphere surface using Fibonacci spiral
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const phi = Math.acos(1 - 2 * (i + 0.5) / PARTICLE_COUNT)
      const theta = Math.PI * (1 + Math.sqrt(5)) * i
      const r = RADIUS * (0.4 + 0.6 * Math.random())

      positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = r * Math.cos(phi)

      // 30% red (#e53e3e at low opacity), 70% white (#f0f0f5 at very low opacity)
      if (Math.random() < 0.3) {
        colors[i * 3]     = 0.898  // r
        colors[i * 3 + 1] = 0.243  // g
        colors[i * 3 + 2] = 0.243  // b
      } else {
        colors[i * 3]     = 0.941
        colors[i * 3 + 1] = 0.941
        colors[i * 3 + 2] = 0.961
      }
    }

    // Pre-compute line segments between nearby particles
    const lineVerts: number[] = []
    // Only check a subset to keep geometry size manageable
    const step = 10
    for (let i = 0; i < PARTICLE_COUNT; i += step) {
      const ax = positions[i * 3]
      const ay = positions[i * 3 + 1]
      const az = positions[i * 3 + 2]
      for (let j = i + step; j < Math.min(i + step * 20, PARTICLE_COUNT); j += step) {
        const dx = ax - positions[j * 3]
        const dy = ay - positions[j * 3 + 1]
        const dz = az - positions[j * 3 + 2]
        if (dx * dx + dy * dy + dz * dz < CONNECTION_DIST * CONNECTION_DIST) {
          lineVerts.push(ax, ay, az, positions[j * 3], positions[j * 3 + 1], positions[j * 3 + 2])
        }
      }
    }

    return {
      positions,
      colors,
      linePositions: new Float32Array(lineVerts),
    }
  }, [])

  useFrame(() => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += 0.0003
      pointsRef.current.rotation.x += 0.0001
    }
    if (linesRef.current) {
      linesRef.current.rotation.y += 0.0003
      linesRef.current.rotation.x += 0.0001
    }
  })

  return (
    <>
      <points ref={pointsRef}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[positions, 3]}
          />
          <bufferAttribute
            attach="attributes-color"
            args={[colors, 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.015}
          vertexColors
          transparent
          opacity={0.5}
          sizeAttenuation
        />
      </points>

      {linePositions.length > 0 && (
        <lineSegments ref={linesRef}>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              args={[linePositions, 3]}
            />
          </bufferGeometry>
          <lineBasicMaterial
            color="#e53e3e"
            transparent
            opacity={0.08}
          />
        </lineSegments>
      )}
    </>
  )
}
