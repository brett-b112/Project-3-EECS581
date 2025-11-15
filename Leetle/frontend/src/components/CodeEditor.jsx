import React, { useState, useEffect } from 'react'
import Editor from '@monaco-editor/react'

export default function CodeEditor({ value, onChange, language, onRun }){
  const [theme, setTheme] = useState('light')

  // Load saved theme preference
  useEffect(() => {
    const savedTheme = localStorage.getItem('code-editor-theme') || 'light'
    setTheme(savedTheme)
  }, [])

  // Autosave functionality
  useEffect(() => {
    const autosaveInterval = setInterval(() => {
      if (value && value.trim()) {
        const key = `leetle-autosave-${language}`
        localStorage.setItem(key, JSON.stringify({
          code: value,
          language: language,
          timestamp: Date.now()
        }))
      }
    }, 10000) // Autosave every 10 seconds

    return () => clearInterval(autosaveInterval)
  }, [value, language])

  // Load autosaved code on mount
  useEffect(() => {
    const key = `leetle-autosave-${language}`
    const saved = localStorage.getItem(key)
    if (saved) {
      try {
        const data = JSON.parse(saved)
        // Only load if it's recent (within last hour)
        if (Date.now() - data.timestamp < 3600000 && !value) {
          onChange && onChange(data.code)
        }
      } catch (e) {
        console.debug('Could not load autosaved code', e)
      }
    }
  }, [language]) // Only run when language changes

  // Monaco onChange provides (value, event)
  function handleChange(v){
    onChange && onChange(typeof v === 'string' ? v : '')
  }

  function handleMount(editor, monaco){
    // Add keyboard shortcut: Ctrl/Cmd + Enter to run
    try{
      if(onRun && editor && monaco){
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
          onRun()
        })
      }
    }catch(e){
      // ignore if monaco API differs in environment
      console.debug('Could not register run shortcut', e)
    }

    // Configure theme
    if (theme === 'dark') {
      monaco.editor.setTheme('vs-dark')
    } else {
      monaco.editor.setTheme('light')
    }

    // Add custom theme for light mode (better than default)
    monaco.editor.defineTheme('leetle-light', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '008000', fontStyle: 'italic' },
        { token: 'keyword', foreground: '0000FF' },
        { token: 'string', foreground: 'A31515' },
        { token: 'number', foreground: '09885A' }
      ],
      colors: {
        'editor.background': '#fafafa',
        'editor.foreground': '#000000',
        'editor.lineHighlightBackground': '#f0f0f0',
        'editor.selectionBackground': '#ADD6FF',
        'editor.inactiveSelectionBackground': '#E5EBF1'
      }
    })

    if (theme === 'light') {
      monaco.editor.setTheme('leetle-light')
    }
  }

  // Theme toggle handler
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('code-editor-theme', newTheme)
  }

  return (
    <div className="border rounded overflow-hidden">
      {/* Theme toggle button */}
      <div className="bg-gray-100 dark:bg-gray-800 p-2 flex justify-between items-center">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Theme: {theme} • Autosave: On
        </div>
        <button
          onClick={toggleTheme}
          className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          {theme === 'light' ? '🌙 Dark' : '☀️ Light'}
        </button>
      </div>

      <Editor
        height="400px"
        defaultLanguage={language}
        language={language}
        value={value}
        onChange={handleChange}
        onMount={handleMount}
        theme={theme === 'dark' ? 'vs-dark' : 'leetle-light'}
        options={{
          fontSize: 14,
          minimap: { enabled: true, size: 'proportional' },
          smoothScrolling: true,
          wordWrap: 'on',
          formatOnType: true,
          formatOnPaste: true,
          folding: true,
          automaticLayout: true,
          tabSize: 4,
          insertSpaces: true,
          renderWhitespace: 'selection',
          bracketMatching: 'always',
          autoClosingBrackets: 'always',
          autoClosingQuotes: 'always',
          autoIndent: 'full',
          suggestOnTriggerCharacters: true,
          acceptSuggestionOnEnter: 'on',
          quickSuggestions: true
        }}
      />
    </div>
  )
}
