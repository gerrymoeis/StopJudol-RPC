**Prompt for AI Coder Agent:**  

---

**Project Conversion Guide: StopJudol to JSON-RPC Architecture**  
**Objective:** Convert the existing monolithic StopJudol application into a client-server JSON-RPC system. Follow the steps below meticulously. Always verify the current codebase structure and dependencies before implementing changes. Update `context.md` after completing each step.  

---

### **Step 1: Install Required Dependencies**  
**Action:**  
```bash  
# Setup Virtual Environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
# source venv/bin/activate

# Server Dependencies  
pip install jsonrpcserver aiohttp python-dotenv marshmallow pyjwt  

# Client Dependencies (retain existing PyQt6 dependencies)  
pip install jsonrpcclient requests  
```  
**Verify:**  
- Update `requirements.txt` with the new dependencies.  
- Ensure no version conflicts with existing packages.  
- All dependencies should be installed in the virtual environment at `stopjudol/venv/`.
- For running or testing, always use Python from the virtual environment (`venv/Scripts/python.exe` on Windows).  

---

### **Step 2: Restructure the Project Folder**  
**Action:**  
Reorganize the project into three primary components:  
```  
stopjudol/  
├── client/                  # PyQt6 GUI (RPC Client)  
│   ├── src/                 # Retain UI logic from original app.py  
│   └── requirements.txt     # Client-specific dependencies  
├── server/                  # JSON-RPC Server  
│   ├── core/                # Move youtube_api.py, analysis.py, config_manager.py here  
│   ├── rpc/                 # RPC handlers and utilities  
│   ├── .env                 # Store API keys and secrets  
│   └── requirements.txt     # Server-specific dependencies  
└── shared/                  # Shared resources  
    ├── schemas/             # Marshmallow schemas for data serialization  
    └── utils/               # helpers.py, logger_config.py  
```  
**Modify/Delete:**  
- Move `youtube_api.py`, `analysis.py`, and `config_manager.py` to `server/core/`.  
- Move `app.py` (GUI) to `client/src/` and rename to `client.py`.  
- Delete redundant copies of files after verification.  

---

### **Step 3: Implement the JSON-RPC Server**  
**Action:**  
1. Create `server/rpc/handler.py`:  
   ```python  
   from jsonrpcserver import method  
   from core.youtube_api import YouTubeAPI  
   from core.analysis import CommentAnalyzer  

   @method  
   async def fetch_comments(video_id: str) -> dict:  
       return YouTubeAPI().get_comments(video_id)  

   @method  
   async def delete_comment(comment_id: str) -> dict:  
       return YouTubeAPI().delete_comment(comment_id)  
   ```  

2. Create `server/main.py`:  
   ```python  
   from aiohttp import web  
   from jsonrpcserver import async_dispatch  
   from rpc.handler import *  

   async def handle_rpc(request):  
       return web.Response(text=await async_dispatch(await request.text()))  

   app = web.Application()  
   app.router.add_post("/rpc", handle_rpc)  
   web.run_app(app, port=5000)  
   ```  
**Update:**  
- Modify `config_manager.py` to load configurations from `server/.env`.  
- Remove direct YouTube API calls from the client code.  

---

### **Step 4: Adapt the Client to Use JSON-RPC**  
**Action:**  
1. In `client/src/client.py`, replace YouTube API calls with RPC requests:  
   ```python  
   from jsonrpcclient import request  

   def get_comments(self, video_id):  
       response = request("http://localhost:5000/rpc", "fetch_comments", video_id=video_id)  
       return response.data.result  
   ```  

2. Update authentication logic to fetch tokens from the server.  

**Critical Modifications:**  
- Remove all instances of `YouTubeAPI` and `OAuthHandler` from the client.  
- Ensure the client only handles UI events and RPC communication.  

---

### **Step 5: Secure RPC Endpoints**  
**Action:**  
1. Implement JWT authentication in `server/rpc/auth.py`:  
   ```python  
   import jwt  
   from aiohttp import web  

   def authenticate(token: str) -> bool:  
       try:  
           payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])  
           return True  
       except:  
           return False  
   ```  

2. Add authentication middleware to `server/main.py`.  

**Update:**  
- Store sensitive data (e.g., YouTube API credentials) in `server/.env`.  

---

### **Step 6: Error Handling & Logging**  
**Action:**  
1. Add RPC-specific error codes in `server/rpc/errors.py`:  
   ```python  
   RPC_ERRORS = {  
       401: "Unauthorized",  
       403: "YouTube API Quota Exceeded",  
       404: "Comment Not Found"  
   }  
   ```  

2. Update `logger_config.py` to log RPC requests/responses.  

---

### **Step 7: Testing & Validation**  
**Action:**  
1. Start the server:  
   ```bash  
   python -m server.main  
   ```  

2. Run the client:  
   ```bash  
   python -m client.src.client  
   ```  

3. Verify:  
   - Comment fetching/deletion works via RPC.  
   - All GUI functionality is retained.  
   - Errors are logged and propagated correctly.  

---

### **Step 8: Update Documentation**  
**Action:**  
1. Update `context.md` with:  
   - New folder structure.  
   - RPC endpoint documentation.  
   - Deployment instructions for client/server.  

2. Remove obsolete documentation related to the monolithic architecture.  

---

**Final Instructions for AI Agent:**  
- Cross-reference each step with the current codebase to avoid conflicts.  
- Test after every file modification. 
- Prioritize incremental changes over large-scale rewrites.