// File Description:
// This file defines a reusable CodeEditor component that provides an interactive Monaco-based code editor
// with autosave, theme switching, keyboard shortcuts, and automatic layout adjustments. It handles reading
// and writing user preferences and autosaved code, configuring Monaco themes, and exposing callbacks for
// parent components. Authors: Daniel Neugent, Brett Balquist, Tej Gumaste, Jay Patel, and Arnav Jain.

import React, { useState, useEffect } from 'react'
import Editor from '@monaco-editor/react'

export default function CodeEditor({ value, onChange, language, onRun }){
  // Function Description:
  // Main exported component that renders the code editor, manages theme state, autosave logic, and event handlers.
  // Inputs: value (string), onChange (function), language (string), onRun (function)
  // Output: JSX element containing configured Monaco editor
  // Contributors: Daniel Neugent, Tej Gumaste, Arnav Jain
  const [theme, setTheme] = useState('light')

  // Load saved theme preference
  // Function Description:
  // Loads previously saved theme from localStorage and updates state.
  // Inputs: none
  // Output: none
  // Contributors: Brett Balquist, Jay Patel
  useEffect(() => {
    const savedTheme = localStorage.getItem('code-editor-theme') || 'light'
    setTheme(savedTheme)
  }, [])

  // Autosave functionality
  // Function Description:
  // Automatically saves the user's current code to localStorage every 10 seconds.
  // Inputs: value (string), language (string)
  // Output: none
  // Contributors: Daniel Neugent, Brett Balquist
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
    }, 10000)

    return () => clearInterval(autosaveInterval)
  }, [value, language])

  // Load autosaved code on mount
  // Function Description:
  // Loads recently stored autosaved code (within last hour) if available and current editor is empty.
  // Inputs: language (string)
  // Output: none
  // Contributors: Tej Gumaste, Jay Patel
  useEffect(() => {
    const key = `leetle-autosave-${language}`
    const saved = localStorage.getItem(key)
    if (saved) {
      try {
        const data = JSON.parse(saved)
        if (Date.now() - data.timestamp < 3600000 && !value) {
          onChange && onChange(data.code)
        }
      } catch (e) {
        console.debug('Could not load autosaved code', e)
      }
    }
  }, [language])

  // Monaco onChange provides (value, event)
  // Function Description:
  // Handles editor changes and forwards updated code to parent onChange callback.
  // Inputs: v (string)
  // Output: none
  // Contributors: Jay Patel, Arnav Jain
  function handleChange(v) {
    onChange && onChange(typeof v === 'string' ? v : '')
  }

  // Function Description:
  // Runs when Monaco editor mounts. Registers keyboard shortcuts, applies themes, and defines a custom theme.
  // Inputs: editor (Monaco editor instance), monaco (monaco namespace)
  // Output: none
  // Contributors: Daniel Neugent, Brett Balquist, Tej Gumaste
  function handleMount(editor, monaco) {
    try {
      if (onRun && editor && monaco) {
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
          onRun()
        })
      }
    } catch (e) {
      console.debug('Could not register run shortcut', e)
    }

    if (theme === 'dark') {
      monaco.editor.setTheme('vs-dark')
    } else {
      monaco.editor.setTheme('light')
    }

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
  // Function Description:
  // Switches between light and dark editor themes and saves selection.
  // Inputs: none
  // Output: none
  // Contributors: Arnav Jain, Tej Gumaste
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('code-editor-theme', newTheme)
  }

  return (
    <div className="border rounded overflow-hidden">
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

