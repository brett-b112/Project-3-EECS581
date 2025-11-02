import React, {useEffect} from 'react'

export default function Toast({id, message, type='info', onClose}){
  useEffect(()=>{
    const t = setTimeout(()=> onClose && onClose(id), 3000)
    return ()=> clearTimeout(t)
  }, [id, onClose])

  const colors = {
    info: 'bg-indigo-600',
    success: 'bg-green-600',
    error: 'bg-red-600'
  }

  return (
    <div className={`px-4 py-2 rounded shadow text-white ${colors[type]||colors.info} fade-in`}>
      {message}
    </div>
  )
}
