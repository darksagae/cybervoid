'use client';

import React, { useState, useEffect } from 'react';
import styles from './page.module.css';

const CATEGORIES = [
  { name: 'Information Gathering', short: 'INFO GATHER', count: 10, color: '#00ffc3', tag: 'DEV' },
  { name: 'Vulnerability Analysis', short: 'VULN ANALYSIS', count: 6, color: '#ff4d4d', tag: 'VUL' },
  { name: 'Web Application Analysis', short: 'WEB APP', count: 10, color: '#ffcc00', tag: 'WEB' },
  { name: 'Database Assessment', short: 'DB ASSESS', count: 6, color: '#00ff7f', tag: 'DB' },
  { name: 'Password Attacks', short: 'PASSWORDS', count: 7, color: '#ff66cc', tag: 'PWD' },
  { name: 'Wireless Attacks', short: 'WIRELESS', count: 7, color: '#00ffff', tag: 'WIF' },
  { name: 'Reverse Engineering', short: 'REV ENG', count: 8, color: '#b366ff', tag: 'REV' },
  { name: 'Exploitation Tools', short: 'EXPLOIT', count: 6, color: '#ff3333', tag: 'EXP' },
  { name: 'Sniffing & Spoofing', short: 'SNIFF/SPOOF', count: 7, color: '#3399ff', tag: 'NET' },
  { name: 'Post Exploitation', short: 'POST EXPLOIT', count: 7, color: '#ff9933', tag: 'PEX' },
  { name: 'Forensics', short: 'FORENSICS', count: 8, color: '#99ff66', tag: 'FOR' },
  { name: 'Social Engineering', short: 'SOC ENG', count: 5, color: '#ff8c00', tag: 'SOC' },
  { name: 'AI Assistant', short: 'AI ASSIST', count: 'A', color: '#a066ff', tag: 'AI' },
];

const TOOLS = [
  { id: 'nmap', name: 'nmap', desc: 'Network mapper & service scanner', icon: '' },
  { id: 'theHarvester', name: 'theHarvester', desc: 'Email, subdomain & name harvester', icon: '' },
  { id: 'whois', name: 'whois', desc: 'Domain registration lookup', icon: '' },
  { id: 'dig', name: 'dig', desc: 'DNS query & zone enumeration', icon: '' },
  { id: 'amass', name: 'amass', desc: 'Attack surface & subdomain mapper', icon: '' },
  { id: 'subfinder', name: 'subfinder', desc: 'Fast passive subdomain discovery', icon: '' },
  { id: 'shodan', name: 'shodan', desc: 'IoT / exposed service search', icon: '' },
  { id: 'recon-ng', name: 'recon-ng', desc: 'Full-featured recon framework', icon: '' },
];

const RECENT_ACTIVITY = [
  { tool: 'wifite', target: 'Telciomy', status: 'success', cmd: 'wifite --kill' },
  { tool: 'nmap', target: '192.168.1.1', status: 'success', cmd: 'nmap -sV -T4' },
  { tool: 'sqlmap', target: 'example.com', status: 'pending', cmd: 'sqlmap -u ...' },
];

export default function Home() {
  const [selectedCategory, setSelectedCategory] = useState('INFO GATHER');
  const [selectedTool, setSelectedTool] = useState('nmap');
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <main className={styles.container}>
      <div className="scan-beam" />
      
      {/* Header Area */}
      <header className={styles.header}>
        <div className={styles.title}>
          <span className={styles.brand}>CYBERVOID</span>
          <span>COMMAND CENTRE</span>
        </div>
        
        <div className={styles.systemStats}>
          <div className={styles.statItem}><span className={styles.statLabel}>CMDS:</span> <span className={styles.statValue}>124</span></div>
          <div className={styles.statItem}><span className={styles.statLabel}>TGTS:</span> <span className={styles.statValue}>12</span></div>
          <div className={styles.statItem}><span className={styles.statLabel}>TIME:</span> <span className={styles.statValue}>{time.toLocaleTimeString()}</span></div>
        </div>

        <div className={styles.headerIcons}>
          <div className={styles.iconBox}></div>
          <div className={styles.iconBox}></div>
          <div className={styles.iconBox}></div>
          <div className={styles.iconBox}></div>
        </div>
      </header>

      <div className={styles.content}>
        {/* Navigation Sidebar */}
        <aside className={styles.sidebar}>
          {CATEGORIES.map((cat) => (
            <button
              key={cat.short}
              className={`${styles.categoryCard} ${selectedCategory === cat.short ? styles.activeCategory : ''}`}
              onClick={() => setSelectedCategory(cat.short)}
              style={{ 
                '--cat-color': cat.color,
                '--cat-color-glow': `${cat.color}33` 
              } as any}
            >
              <div className={styles.catTag}>{cat.tag}</div>
              <div className={styles.catName}>
                {cat.short}
                <span className={styles.catCount}>{cat.count !== null ? `[${cat.count}]` : ''}</span>
              </div>
            </button>
          ))}
        </aside>

        {/* Main Orchestration Panel */}
        <section className={styles.mainSection}>
          <div className={styles.panel}>
            <div className={styles.panelHeader}>
              <h2 className={styles.panelTitle}>INFORMATION GATHERING</h2>
              <div className={styles.badge}>SCANNING ACTIVE</div>
            </div>

            <div className={styles.toolGrid}>
              {TOOLS.map((tool) => (
                <button
                  key={tool.id}
                  className={`${styles.toolButton} ${selectedTool === tool.id ? styles.activeTool : ''}`}
                  onClick={() => setSelectedTool(tool.id)}
                >
                  <div className={styles.toolIcon}>{tool.icon}</div>
                  <div className={styles.toolMeta}>
                    <h3>{tool.name}</h3>
                    <p>{tool.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Console & Activity Area */}
          <div className={styles.bottomArea}>
            <div className={styles.consoleBox}>
              <div className={styles.fieldRow}>
                <label>CMD:</label>
                <input type="text" className={styles.textInput} placeholder="Enter command parameters..." />
              </div>
              <div className={styles.fieldRow}>
                <label>TARGET:</label>
                <select className={styles.textInput}>
                  <option>Select Active Target...</option>
                  <option>192.168.1.1</option>
                  <option>10.0.0.5</option>
                  <option>victim-site.com</option>
                </select>
              </div>
              <div className={styles.buttonRow}>
                <button className={styles.executeBtn}>INITIATE COMMAND</button>
              </div>
            </div>

            <div className={styles.activityBox}>
              <div className={styles.activityHeader}>
                <h3>RECENT ACTIVITY LOG</h3>
                <div className={styles.dots}>•••</div>
              </div>
              <div className={styles.logScroll}>
                {RECENT_ACTIVITY.map((act, i) => (
                  <div key={i} className={styles.logItem}>
                    <span className={styles.logCmd}>{act.tool}</span>
                    <span className={styles.logLabel}>command:</span>
                    <span className={styles.logTarget}>{act.target}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
