from flask import Flask, render_template, request, redirect, url_for, make_response
import sqlite3, csv, io
from datetime import datetime

app = Flask(__name__)
DB = "bridges.db"

TEAM = [
    {"name":"Сайби Ахмед Ясин","short":"UI / Frontend","role":"Разработка пользовательского интерфейса","work":"Проектирование интерфейса, навигации, карточек объектов, форм, интерактивных элементов и адаптивной вёрстки."},
    {"name":"Хашпаков Амир Бесланович","short":"Data Collection","role":"Разработка модуля сбора данных","work":"Ввод и регистрация данных о мостах, результаты обследований, параметры сооружений и первичная фиксация дефектов."},
    {"name":"Кубикильма Нсинги Лонги","short":"Analytics","role":"Разработка модуля анализа данных","work":"Расчёт индекса состояния, оценка риска, агрегирование показателей и подготовка аналитических выводов."},
    {"name":"Саного Хабибату","short":"Visualization","role":"Разработка модуля визуализации данных","work":"Диаграммы, KPI, динамика состояния, визуальные индикаторы и представление результатов мониторинга."},
    {"name":"Тиффо Тепуно Гаррис Джовик","short":"Reporting","role":"Разработка модуля формирования отчётности","work":"Сводные отчёты, экспорт данных, печатные формы и подготовка информации по объектам."}
]

BRIDGES = [
("Крымский мост","Москва, Центральный административный округ",1938,"2026-09-26","Хорошее","Низкий",91,"Автодорожный мост","Сталь и железобетон",688,37.0,6,55.7304,37.5950,"Крупное транспортное сооружение через Москву-реку. В учебной системе объект используется для демонстрации мониторинга, истории осмотров и геопривязки."),
("Большой Каменный мост","Москва, Кремлёвская набережная",1938,"2026-09-24","Хорошее","Низкий",86,"Автодорожный мост","Железобетон",487,40.0,6,55.7468,37.6100,"Городской мост в центральной части Москвы. Контроль включает состояние покрытия, конструкций и результаты плановых обследований."),
("Большой Москворецкий мост","Москва, Москворецкая набережная",1938,"2026-09-23","Требует внимания","Средний",67,"Автодорожный мост","Сталь и железобетон",554,40.0,8,55.7490,37.6270,"Интенсивно используемый городской объект. Для демонстрационного мониторинга отмечен средний уровень риска."),
("Лужнецкий мост","Москва, Лужники",1958,"2026-09-21","Хорошее","Низкий",89,"Автодорожный мост","Железобетон",203,28.0,6,55.7138,37.5535,"Транспортный объект в районе Лужников. Высокий текущий индекс состояния по демонстрационным данным."),
("Новоспасский мост","Москва, Новоспасская набережная",1911,"2026-09-19","Требует внимания","Средний",61,"Автодорожный мост","Сталь и железобетон",140,25.0,4,55.7287,37.6573,"Историческое сооружение. В карточке предусмотрена расширенная история обследований и фиксация дефектов."),
("Андреевский мост","Москва, Воробьёвы горы",1905,"2026-09-18","Хорошее","Низкий",82,"Железнодорожный мост","Сталь",135,18.0,2,55.7088,37.5638,"Мост в районе Воробьёвых гор. Используется как объект для сравнения разных типов сооружений."),
("Багратионовский мост","Москва, Пресненская набережная",1997,"2026-09-16","Хорошее","Низкий",95,"Пешеходный мост","Сталь и стекло",214,12.0,0,55.7483,37.5380,"Современное сооружение. Высокий индекс состояния в демонстрационном наборе."),
("Пушкинский мост","Москва, Пушкинская набережная",2000,"2026-09-14","Требует внимания","Средний",58,"Пешеходный мост","Сталь",214,10.0,0,55.7227,37.5728,"Пешеходное сооружение. В системе используется для демонстрации отдельных критериев риска и состояния."),
("Северный мост","Москва, Ленинградское шоссе",1983,"2026-09-12","Критическое","Высокий",34,"Автодорожный мост","Железобетон",310,24.0,6,55.8355,37.4930,"Учебный сценарий с низким индексом состояния. Требуется приоритетное обследование и контроль дефектов."),
("Мост через Яузу","Москва, Ростокинская набережная",1976,"2026-09-10","Требует внимания","Средний",72,"Автодорожный мост","Железобетон",118,19.0,4,55.8201,37.6651,"Демонстрационный объект для сравнения результатов регулярных обследований.")
]

INSPECTIONS = [
(1,"2026-09-26","Хашпаков Амир Бесланович",91,"Незначительный износ покрытия","Плановый визуальный осмотр. Критических дефектов не выявлено."),
(1,"2026-06-18","Хашпаков Амир Бесланович",88,"Локальные следы износа","Рекомендуется продолжить плановый контроль."),
(2,"2026-09-24","Хашпаков Амир Бесланович",86,"Поверхностные дефекты покрытия","Состояние контролируемое."),
(2,"2026-05-20","Хашпаков Амир Бесланович",82,"Незначительные трещины","Без критических замечаний."),
(3,"2026-09-23","Хашпаков Амир Бесланович",67,"Локальные трещины покрытия","Рекомендуется усиленный контроль."),
(3,"2026-04-14","Хашпаков Амир Бесланович",71,"Износ покрытия","Плановый ремонт покрытия рекомендуется."),
(4,"2026-09-21","Хашпаков Амир Бесланович",89,"Не выявлены","Состояние стабильное."),
(5,"2026-09-19","Хашпаков Амир Бесланович",61,"Следы коррозии и износ покрытия","Нужен контроль и повторное обследование."),
(6,"2026-09-18","Хашпаков Амир Бесланович",82,"Локальный износ","Состояние удовлетворительное."),
(7,"2026-09-16","Хашпаков Амир Бесланович",95,"Не выявлены","Состояние хорошее."),
(8,"2026-09-14","Хашпаков Амир Бесланович",58,"Износ элементов покрытия","Рекомендуется дополнительный осмотр."),
(9,"2026-09-12","Хашпаков Амир Бесланович",34,"Трещины, коррозионные участки","Приоритетная техническая проверка."),
(10,"2026-09-10","Хашпаков Амир Бесланович",72,"Локальный износ","Наблюдение в рамках планового цикла.")
]

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def condition_from_score(score):
    if score >= 80: return "Хорошее","Низкий"
    if score >= 50: return "Требует внимания","Средний"
    return "Критическое","Высокий"

def yandex_url(lat, lon):
    return f"https://yandex.ru/maps/?ll={lon},{lat}&z=16&l=map&pt={lon},{lat},pm2rdm"

def init_db():
    c=db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS bridges(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,location TEXT NOT NULL,year INTEGER NOT NULL,last_inspection TEXT NOT NULL,condition TEXT NOT NULL,risk TEXT NOT NULL,score INTEGER NOT NULL,bridge_type TEXT DEFAULT 'Автодорожный мост',material TEXT DEFAULT 'Железобетон',length REAL DEFAULT 0,width REAL DEFAULT 0,lanes INTEGER DEFAULT 2,latitude REAL DEFAULT 55.7558,longitude REAL DEFAULT 37.6173,description TEXT DEFAULT '');
    CREATE TABLE IF NOT EXISTS inspections(id INTEGER PRIMARY KEY AUTOINCREMENT,bridge_id INTEGER NOT NULL,date TEXT NOT NULL,inspector TEXT NOT NULL,score INTEGER NOT NULL,defects TEXT,notes TEXT,FOREIGN KEY(bridge_id) REFERENCES bridges(id));
    """)
    cols={r[1] for r in c.execute("PRAGMA table_info(bridges)").fetchall()}
    for col,definition in {"bridge_type":"TEXT DEFAULT 'Автодорожный мост'","material":"TEXT DEFAULT 'Железобетон'","length":"REAL DEFAULT 0","width":"REAL DEFAULT 0","lanes":"INTEGER DEFAULT 2","latitude":"REAL DEFAULT 55.7558","longitude":"REAL DEFAULT 37.6173","description":"TEXT DEFAULT ''"}.items():
        if col not in cols: c.execute(f"ALTER TABLE bridges ADD COLUMN {col} {definition}")
    count=c.execute("SELECT COUNT(*) FROM bridges").fetchone()[0]
    names=[r[0] for r in c.execute("SELECT name FROM bridges").fetchall()]
    expected_names={b[0] for b in BRIDGES}
    if count < len(BRIDGES) or not expected_names.issubset(set(names)):
        c.execute("DELETE FROM inspections"); c.execute("DELETE FROM bridges")
        c.executemany("INSERT INTO bridges(name,location,year,last_inspection,condition,risk,score,bridge_type,material,length,width,lanes,latitude,longitude,description) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",BRIDGES)
        c.executemany("INSERT INTO inspections(bridge_id,date,inspector,score,defects,notes) VALUES(?,?,?,?,?,?)",INSPECTIONS)
    c.commit(); c.close()

@app.context_processor
def globals(): return {"team":TEAM,"project_title":"Веб-приложение для мониторинга состояния мостовых сооружений","now":datetime.now().strftime("%d.%m.%Y %H:%M")}

@app.route('/')
def index():
    c=db(); stats={
        "total":c.execute("SELECT COUNT(*) FROM bridges").fetchone()[0],"good":c.execute("SELECT COUNT(*) FROM bridges WHERE condition='Хорошее'").fetchone()[0],"warning":c.execute("SELECT COUNT(*) FROM bridges WHERE condition='Требует внимания'").fetchone()[0],"critical":c.execute("SELECT COUNT(*) FROM bridges WHERE condition='Критическое'").fetchone()[0],"avg":round(c.execute("SELECT AVG(score) FROM bridges").fetchone()[0] or 0),"inspections":c.execute("SELECT COUNT(*) FROM inspections").fetchone()[0]}
    bridges=c.execute("SELECT * FROM bridges ORDER BY score ASC").fetchall(); recent=c.execute("SELECT i.*,b.name bridge_name FROM inspections i JOIN bridges b ON b.id=i.bridge_id ORDER BY i.date DESC,i.id DESC LIMIT 8").fetchall(); c.close()
    return render_template('index.html',stats=stats,bridges=bridges,recent=recent)

@app.route('/bridges')
def bridges():
    q=request.args.get('q','').strip(); condition=request.args.get('condition',''); typ=request.args.get('type','')
    init_db()
    c=db(); rows=c.execute("SELECT * FROM bridges WHERE (?='' OR name LIKE ? OR location LIKE ? OR bridge_type LIKE ? OR material LIKE ?) AND (?='' OR condition=?) AND (?='' OR bridge_type=?) ORDER BY score ASC",(q,f'%{q}%',f'%{q}%',f'%{q}%',f'%{q}%',condition,condition,typ,typ)).fetchall(); types=c.execute("SELECT DISTINCT bridge_type FROM bridges ORDER BY bridge_type").fetchall(); total=c.execute('SELECT COUNT(*) FROM bridges').fetchone()[0]; c.close()
    return render_template('bridges.html',bridges=rows,q=q,condition=condition,typ=typ,types=types,total=total)

@app.route('/bridge/<int:bridge_id>')
def bridge(bridge_id):
    c=db(); b=c.execute('SELECT * FROM bridges WHERE id=?',(bridge_id,)).fetchone(); ins=c.execute('SELECT * FROM inspections WHERE bridge_id=? ORDER BY date DESC,id DESC',(bridge_id,)).fetchall(); c.close()
    if not b:return 'Мост не найден',404
    return render_template('bridge.html',bridge=b,inspections=ins,map_url=yandex_url(b['latitude'],b['longitude']))

@app.route('/add',methods=['GET','POST'])
def add():
    if request.method=='POST':
        f=request.form; score=max(0,min(100,int(f['score']))); cond,risk=condition_from_score(score); c=db(); c.execute("INSERT INTO bridges(name,location,year,last_inspection,condition,risk,score,bridge_type,material,length,width,lanes,latitude,longitude,description) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(f['name'],f['location'],int(f['year']),f['date'],cond,risk,score,f.get('bridge_type','Автодорожный мост'),f.get('material','Железобетон'),float(f.get('length') or 0),float(f.get('width') or 0),int(f.get('lanes') or 2),float(f.get('latitude') or 55.7558),float(f.get('longitude') or 37.6173),f.get('description',''))); c.commit(); new=c.execute('SELECT last_insert_rowid()').fetchone()[0]; c.close(); return redirect(url_for('bridge',bridge_id=new))
    return render_template('add.html')

@app.route('/inspection/<int:bridge_id>',methods=['POST'])
def inspection(bridge_id):
    f=request.form; score=max(0,min(100,int(f['score']))); cond,risk=condition_from_score(score); c=db(); c.execute('INSERT INTO inspections(bridge_id,date,inspector,score,defects,notes) VALUES(?,?,?,?,?,?)',(bridge_id,f['date'],f['inspector'],score,f.get('defects',''),f.get('notes',''))); c.execute('UPDATE bridges SET last_inspection=?,condition=?,risk=?,score=? WHERE id=?',(f['date'],cond,risk,score,bridge_id)); c.commit(); c.close(); return redirect(url_for('bridge',bridge_id=bridge_id))

@app.route('/analytics')
def analytics():
    c=db(); rows=c.execute("SELECT condition,COUNT(*) AS n,ROUND(AVG(score),1) AS avg FROM bridges GROUP BY condition").fetchall(); types=c.execute("SELECT bridge_type,COUNT(*) AS n FROM bridges GROUP BY bridge_type ORDER BY n DESC").fetchall(); top=c.execute('SELECT * FROM bridges ORDER BY score ASC LIMIT 6').fetchall(); c.close();
    # Convert SQLite Row objects to plain dictionaries so Jinja/Chart.js JSON serialization is reliable.
    rows=[dict(r) for r in rows]; types=[dict(r) for r in types]; top=[dict(r) for r in top]
    return render_template('analytics.html',rows=rows,types=types,top_risk=top)

@app.route('/reports')
def reports():
    c=db(); rows=c.execute('SELECT * FROM bridges ORDER BY score ASC').fetchall(); total=c.execute('SELECT COUNT(*) FROM inspections').fetchone()[0]; c.close(); return render_template('reports.html',bridges=rows,inspection_count=total)

@app.route('/export.csv')
def export_csv():
    c=db(); rows=c.execute('SELECT * FROM bridges ORDER BY id').fetchall(); c.close(); out=io.StringIO(); w=csv.writer(out); w.writerow(['ID','Название','Расположение','Год','Тип','Материал','Длина, м','Ширина, м','Полосы','Широта','Долгота','Последний осмотр','Состояние','Риск','Индекс']);
    for r in rows:w.writerow([r['id'],r['name'],r['location'],r['year'],r['bridge_type'],r['material'],r['length'],r['width'],r['lanes'],r['latitude'],r['longitude'],r['last_inspection'],r['condition'],r['risk'],r['score']])
    resp=make_response('\ufeff'+out.getvalue()); resp.headers['Content-Disposition']='attachment; filename=bridges_report.csv'; resp.headers['Content-Type']='text/csv; charset=utf-8'; return resp

init_db()
if __name__=='__main__': app.run(debug=True)
