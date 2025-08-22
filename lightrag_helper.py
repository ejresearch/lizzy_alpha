#!/usr/bin/env python3
"""
LightRAG Helper Module for Lizzy Alpha
======================================
Provides simplified LightRAG integration with proper initialization.
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from lightrag import LightRAG, QueryParam
from lightrag.llm import gpt_4o_mini_complete, gpt_4o_complete, openai_embedding
from lightrag.utils import set_logger

# Setup logging
set_logger("lightrag")


class LightRAGManager:
    """Manages LightRAG instances for different knowledge buckets."""
    
    def __init__(self, working_dir: str = "./lightrag_working_dir"):
        self.working_dir = Path(working_dir)
        self.instances = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize all available LightRAG buckets."""
        if self.initialized:
            return
            
        # Find available buckets
        valid_buckets = ['books', 'plays', 'scripts']
        bucket_dirs = [d for d in self.working_dir.iterdir() 
                      if d.is_dir() and d.name in valid_buckets]
        
        print(f"🔍 Initializing {len(bucket_dirs)} knowledge buckets...")
        
        for bucket_dir in bucket_dirs:
            try:
                # Create LightRAG instance for this bucket
                rag = LightRAG(
                    working_dir=str(bucket_dir),
                    embedding_func=openai_embedding,
                    llm_model_func=gpt_4o_mini_complete,
                )
                
                self.instances[bucket_dir.name] = rag
                print(f"  ✅ Loaded: {bucket_dir.name}")
                
            except Exception as e:
                print(f"  ❌ Failed to load {bucket_dir.name}: {e}")
        
        self.initialized = True
        print(f"✅ Initialized {len(self.instances)} buckets")
    
    async def query_bucket(self, bucket_name: str, query: str, mode: str = "hybrid") -> str:
        """Query a specific knowledge bucket."""
        if not self.initialized:
            await self.initialize()
        
        if bucket_name not in self.instances:
            return f"Bucket '{bucket_name}' not available"
        
        try:
            rag = self.instances[bucket_name]
            result = await rag.aquery(
                query,
                param=QueryParam(mode=mode)
            )
            return result
        except Exception as e:
            return f"Query error: {e}"
    
    async def query_all_buckets(self, query: str, mode: str = "hybrid") -> Dict[str, str]:
        """Query all available buckets and return results."""
        if not self.initialized:
            await self.initialize()
        
        results = {}
        for bucket_name, rag in self.instances.items():
            try:
                result = await rag.aquery(
                    query,
                    param=QueryParam(mode=mode)
                )
                results[bucket_name] = result
            except Exception as e:
                results[bucket_name] = f"Error: {e}"
        
        return results
    
    async def insert_document(self, bucket_name: str, content: str, doc_id: Optional[str] = None):
        """Insert a document into a specific bucket."""
        if not self.initialized:
            await self.initialize()
        
        if bucket_name not in self.instances:
            raise ValueError(f"Bucket '{bucket_name}' not available")
        
        rag = self.instances[bucket_name]
        if doc_id:
            await rag.ainsert(content, doc_id=doc_id)
        else:
            await rag.ainsert(content)
        
        print(f"✅ Document inserted into {bucket_name}")
    
    async def finalize(self):
        """Clean up and close all connections."""
        for bucket_name, rag in self.instances.items():
            try:
                await rag.finalize_storages()
            except:
                pass
        self.initialized = False


class CreativeQueryBuilder:
    """Builds creative queries for storytelling contexts."""
    
    @staticmethod
    def build_scene_query(scene_data: dict, tone: str) -> str:
        """Build a query for scene development."""
        return f"""
        For a {tone} story:
        
        Scene: {scene_data.get('scene_title', 'Untitled')}
        Characters: {scene_data.get('characters_present', 'Unknown')}
        Key Events: {scene_data.get('key_events', 'Not specified')}
        
        Provide creative ideas for:
        1. Opening that hooks the reader
        2. Character interactions and dialogue
        3. Emotional beats and tension
        4. Sensory details and atmosphere
        5. Scene conclusion that propels the story
        """
    
    @staticmethod
    def build_character_query(character_data: dict, tone: str) -> str:
        """Build a query for character development."""
        return f"""
        For a {tone} story character:
        
        Name: {character_data.get('name', 'Unknown')}
        Role: {character_data.get('role', 'Not specified')}
        Traits: {character_data.get('personality_traits', 'Not specified')}
        Goals: {character_data.get('goals', 'Not specified')}
        
        Provide insights on:
        1. Unique mannerisms and speech patterns
        2. Internal conflicts and motivations
        3. Character arc and growth opportunities
        4. Relationships with other characters
        5. Memorable moments that reveal personality
        """
    
    @staticmethod
    def build_plot_query(plot_focus: str, story_context: str, tone: str) -> str:
        """Build a query for plot development."""
        return f"""
        For a {tone} story focusing on {plot_focus}:
        
        Story Context:
        {story_context}
        
        Generate ideas for:
        1. Plot twists and surprises
        2. Rising tension and conflict
        3. Character-driven complications
        4. Thematic resonance
        5. Satisfying resolution elements
        """


async def test_lightrag_integration():
    """Test the LightRAG integration."""
    print("🧪 Testing LightRAG Integration")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ Please set your OPENAI_API_KEY in the .env file")
        return False
    
    # Initialize manager
    manager = LightRAGManager()
    
    try:
        await manager.initialize()
        
        # Test query on books bucket if available
        if 'books' in manager.instances:
            print("\n📚 Testing query on 'books' bucket...")
            result = await manager.query_bucket(
                'books',
                "What are common themes in romantic comedies?",
                mode="global"
            )
            print(f"Result preview: {result[:200]}..." if len(result) > 200 else result)
            print("✅ Query successful!")
        else:
            print("⚠️  No 'books' bucket available for testing")
        
        await manager.finalize()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        await manager.finalize()
        return False


def main():
    """Main entry point for testing."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run test
    success = asyncio.run(test_lightrag_integration())
    
    if success:
        print("\n✅ LightRAG integration is working!")
        print("You can now use the brainstorm module with AI-powered knowledge retrieval.")
    else:
        print("\n❌ LightRAG integration needs configuration.")
        print("Please check your .env file and ensure OPENAI_API_KEY is set.")


if __name__ == "__main__":
    main()