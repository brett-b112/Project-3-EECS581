import React from 'react'
import Editor from '@monaco-editor/react'

export default function CodeEditor({ value, onChange, language, onRun }){
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
  }

  return (
    <div className="border rounded overflow-hidden">
      <Editor
        height="420px"
        defaultLanguage={language}
        language={language}
        value={value}
        onChange={handleChange}
        onMount={handleMount}
        options={{
          fontSize: 14,
          minimap: { enabled: false },
          smoothScrolling: true,
          wordWrap: 'on',
          formatOnType: true,
          formatOnPaste: true,
          folding: true,
          automaticLayout: true
        }}
      />
    </div>
  )
}
