import { useEffect, useState } from 'react'
import axios from 'axios'
import { Bot, Battery, MapPin, AlertCircle } from 'lucide-react'

interface Robot {
  id: number
  name: string
  battery: number
  status: string
  x: number
  y: number
  task: string | null
}

const API_URL = 'http://localhost:8000'

export default function RobotDashboard() {
  const [robots, setRobots] = useState<Robot[]>([])

  const fetchRobots = async () => {
    try {
      const response = await axios.get(`${API_URL}/robots`)
      setRobots(response.data)
    } catch (error) {
      console.error("Error fetching robots:", error)
    }
  }

  useEffect(() => {
    fetchRobots()
    const interval = setInterval(fetchRobots, 2000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {robots.map(robot => (
          <div key={robot.id} className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center">
                <Bot className="mr-2" /> {robot.name}
              </h2>
              <span className={`px-2 py-1 rounded text-sm ${robot.status === 'Idle' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {robot.status}
              </span>
            </div>
            <div className="space-y-2">
              <p className="flex items-center"><Battery className="mr-2 h-4 w-4" /> Battery: {robot.battery}%</p>
              <p className="flex items-center"><MapPin className="mr-2 h-4 w-4" /> Position: ({robot.x}, {robot.y})</p>
              <p className="flex items-center"><AlertCircle className="mr-2 h-4 w-4" /> Task: {robot.task || 'None'}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
