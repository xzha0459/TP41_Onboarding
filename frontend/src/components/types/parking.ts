export interface ParkingSpot {
  id: string
  lat: number
  lng: number
  status: 'available' | 'occupied' | 'unknown'
  address: string
  restrictions: string[]
  pricing: {
    hourlyRate: number
    maxDuration: number
  }
  accessibility: boolean
  timeLimit: number
}

export interface PredictionData {
  location: string
  timeHorizon: number
  availabilityRate: number
  confidenceLevel: number
}
