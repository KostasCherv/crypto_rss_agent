import os
import sys
from datetime import datetime, timezone, date, timedelta
from dotenv import load_dotenv
from daily_digest_agent import create_daily_digest
from weekly_digest_agent import create_weekly_digest
from monthly_digest_agent import create_monthly_digest

# Load .env secrets
load_dotenv()

def run_daily_digest():
    """Run daily digest agent"""
    print("🌅 Running Daily Digest Agent...")
    print("=" * 50)
    
    try:
        success = create_daily_digest()
        if success:
            print("✅ Daily digest completed successfully!")
            return True
        else:
            print("ℹ️  Daily digest skipped (already exists or no articles)")
            return False
    except Exception as e:
        print(f"❌ Daily digest failed: {e}")
        return False

def run_weekly_digest():
    """Run weekly digest agent"""
    print("📊 Running Weekly Digest Agent...")
    print("=" * 50)
    
    try:
        success = create_weekly_digest()
        if success:
            print("✅ Weekly digest completed successfully!")
            return True
        else:
            print("ℹ️  Weekly digest skipped (already exists or no daily digests)")
            return False
    except Exception as e:
        print(f"❌ Weekly digest failed: {e}")
        return False

def run_monthly_digest():
    """Run monthly digest agent"""
    print("📈 Running Monthly Digest Agent...")
    print("=" * 50)
    
    try:
        success = create_monthly_digest()
        if success:
            print("✅ Monthly digest completed successfully!")
            return True
        else:
            print("ℹ️  Monthly digest skipped (already exists or no weekly digests)")
            return False
    except Exception as e:
        print(f"❌ Monthly digest failed: {e}")
        return False

def run_all_digests():
    """Run all digest agents in sequence"""
    print("🚀 Crypto Digest Orchestrator Starting...")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    results = {
        'daily': False,
        'weekly': False,
        'monthly': False
    }
    
    # Run daily digest
    results['daily'] = run_daily_digest()
    print()
    
    # Run weekly digest
    results['weekly'] = run_weekly_digest()
    print()
    
    # Run monthly digest
    results['monthly'] = run_monthly_digest()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 DIGEST SUMMARY")
    print("=" * 60)
    print(f"🌅 Daily Digest:   {'✅ Success' if results['daily'] else '⏭️  Skipped'}")
    print(f"📊 Weekly Digest: {'✅ Success' if results['weekly'] else '⏭️  Skipped'}")
    print(f"📈 Monthly Digest: {'✅ Success' if results['monthly'] else '⏭️  Skipped'}")
    print("=" * 60)
    print(f"⏰ Completed at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("🏁 All digest agents completed!")
    
    return results

def run_specific_digest(digest_type: str):
    """Run a specific digest type"""
    digest_type = digest_type.lower()
    
    if digest_type == 'daily':
        return run_daily_digest()
    elif digest_type == 'weekly':
        return run_weekly_digest()
    elif digest_type == 'monthly':
        return run_monthly_digest()
    else:
        print(f"❌ Unknown digest type: {digest_type}")
        print("Available types: daily, weekly, monthly, all")
        return False

def main():
    """Main function with command line argument support"""
    if len(sys.argv) > 1:
        digest_type = sys.argv[1]
        if digest_type == 'all':
            run_all_digests()
        else:
            run_specific_digest(digest_type)
    else:
        # Default: run all digests
        run_all_digests()

if __name__ == "__main__":
    main()
