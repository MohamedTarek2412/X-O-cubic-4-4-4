# run_all_tests.py
import subprocess
import sys
import os

def run_test(test_file):
    """تشغيل ملف اختبار واحد وإرجاع النتيجة"""
    try:
        print(f"Running {test_file}...")
        
        # تشغيل ملف الاختبار باستخدام Python
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30  # وقت أقصى 30 ثانية لكل اختبار
        )
        
        if result.returncode == 0:
            print(f"PASS: {test_file}")
            # عرض النتائج التفصيلية
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('    '):
                    print(f"  {line}")
            return True
        else:
            print(f"FAIL: {test_file}")
            # عرض الأخطاء
            if result.stderr:
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"  ERROR: {line}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"FAIL: {test_file} - TIMEOUT")
        return False
    except Exception as e:
        print(f"FAIL: {test_file} - {str(e)}")
        return False

def main():
    """الدالة الرئيسية لتشغيل جميع الاختبارات"""
    print("=" * 50)
    print("STARTING CUBIC GAME TESTS")
    print("=" * 50)
    
    test_files = [
        "test_basic.py",
        "test_ai.py", 
        "test_win_conditions.py",
        "test_performance.py"
    ]
    
    print(f"TOTAL TESTS: {len(test_files)}")
    print("-" * 30)
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            if run_test(test_file):
                passed += 1
            else:
                failed += 1
        else:
            print(f"SKIP: {test_file} - File not found")
            failed += 1
    
    print("=" * 50)
    print("FINAL RESULTS:")
    print(f"  PASSED: {passed}")
    print(f"  FAILED: {failed}")
    print(f"  RATIO: {passed}/{len(test_files)}")
    print("=" * 50)
    
    if failed > 0:
        print("WARNING: Some tests failed, review errors above")
        print("Fix the issues and try running again")
        sys.exit(1)
    else:
        print("SUCCESS: All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()