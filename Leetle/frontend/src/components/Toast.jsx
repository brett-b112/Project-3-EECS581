// Toast component with block comments added for clarity
import React, {useEffect} from 'react'

// The Toast component displays a temporary notification
export default function Toast({id, message, type='info', onClose}){
  // Automatically dismiss the toast after 3 seconds
  useEffect(()=>{
    const t = setTimeout(()=> onClose && onClose(id), 3000)
    return ()=> clearTimeout(t)
  }, [id, onClose])

  // Map toast types to background colors
  const colors = {
    info: 'bg-indigo-600',
    success: 'bg-green-600',
    error: 'bg-red-600'
  }

  // Render the toast with appropriate styling
  return (
    <div className={`px-4 py-2 rounded shadow text-white ${colors[type]||colors.info} fade-in`}>
      {message}
    </div>
  )
}

