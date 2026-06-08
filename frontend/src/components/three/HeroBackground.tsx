import { Canvas } from '@react-three/fiber'
import { ParticleMesh } from './ParticleMesh'
import './HeroBackground.css'

export default function HeroBackground() {
  return (
    <div className="hero-background">
      <Canvas
        frameloop="demand"
        dpr={[1, 1.5]}
        camera={{ position: [0, 0, 5], fov: 60 }}
        gl={{ antialias: false, alpha: true }}
      >
        <ambientLight intensity={0.2} />
        <ParticleMesh />
      </Canvas>
    </div>
  )
}
