import { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import { Bot, Battery, MapPin, AlertCircle, Plus, Square, Zap, Play } from 'lucide-react'

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
const WS_URL = 'ws://localhost:8000/ws'

export default function RobotDashboard() {
  const [robots, setRobots] = useState<Robot[]>([])
  const [newRobotName, setNewRobotName] = useState('')
  const ws = useRef<WebSocket | null>(null)

  const fetchRobots = async () => {
    try {
      const response = await axios.get(`${API_URL}/robots`)
      setRobots(response.data)
    } catch (error) {
      console.error("Error fetching robots:", error)
    }
  }

  const addRobot = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await axios.post(`${API_URL}/robots`, {
        name: newRobotName,
        battery: 100,
        status: 'Moving',
        x: 0,
        y: 0,
        task: null
      })
      setNewRobotName('')
    } catch (error) {
      console.error("Error adding robot:", error)
    }
  }

  const sendCommand = async (robotId: number, command: 'STOP' | 'CHARGE' | 'RESUME') => {
    try {
      await axios.put(`${API_URL}/robots/${robotId}`, {
        status: command === 'STOP' ? 'Stopped' : command === 'CHARGE' ? 'Charging' : 'Moving'
      })
    } catch (error) {
      console.error(`Error sending ${command} command:`, error)
    }
  }

  useEffect(() => {
    fetchRobots()

    let reconnectTimeout: ReturnType<typeof setTimeout>

    const connectWebSocket = () => {
      ws.current = new WebSocket(WS_URL)

      ws.current.onopen = () => {
        console.log('WebSocket connected')
      }

      ws.current.onmessage = (event) => {
        const updatedRobot = JSON.parse(event.data)
        setRobots(prevRobots => prevRobots.map(robot =>
          robot.id === updatedRobot.id ? { ...robot, ...updatedRobot } : robot
        ))
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.current.onclose = () => {
        console.log('WebSocket disconnected, reconnecting in 3s...')
        reconnectTimeout = setTimeout(connectWebSocket, 3000)
      }
    }

    connectWebSocket()

    return () => {
      clearTimeout(reconnectTimeout)
      ws.current?.close()
    }
  }, [])

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      <form onSubmit={addRobot} className="mb-6 flex gap-2">
        <input
          type="text"
          value={newRobotName}
          onChange={(e) => setNewRobotName(e.target.value)}
          placeholder="New Robot Name"
          className="p-2 border rounded"
        />
        <button type="submit" className="bg-blue-500 text-white p-2 rounded flex items-center">
          <Plus className="mr-1 h-4 w-4" /> Add Robot
        </button>
      </form>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {robots.map(robot => (
          <div key={robot.id} className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center">
                <Bot className="mr-2" /> {robot.name}
              </h2>
              <span className={`px-2 py-1 rounded text-sm ${robot.status === 'Stopped' ? 'bg-red-100 text-red-800' : robot.status === 'Charging' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'}`}>
                {robot.status}
              </span>
            </div>
            <div className="space-y-2 mb-4">
              <p className="flex items-center"><Battery className="mr-2 h-4 w-4" /> Battery: {robot.battery}%</p>
              <p className="flex items-center"><MapPin className="mr-2 h-4 w-4" /> Position: ({robot.x}, {robot.y})</p>
              <p className="flex items-center"><AlertCircle className="mr-2 h-4 w-4" /> Task: {robot.task || 'None'}</p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => sendCommand(robot.id, 'STOP')} className="bg-red-500 text-white p-2 rounded"><Square size={16} /></button>
              <button onClick={() => sendCommand(robot.id, 'CHARGE')} className="bg-purple-500 text-white p-2 rounded"><Zap size={16} /></button>
              <button onClick={() => sendCommand(robot.id, 'RESUME')} className="bg-green-500 text-white p-2 rounded"><Play size={16} /></button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
