<?php
namespace App\Http\Controllers;
use App\Models\Category;
use Illuminate\Http\Request;

class CategoryController extends Controller
{
    public function categories(){
        $categories = Category::paginate(4);
        return view('admin.dynamcomps.categories', compact('categories'));
    }
    public function addCategory(Request $request){
        $input = $request->validate([
            'category_name' => 'required|string|unique:categories,category_name'
        ],[
            'category_name.required' => 'the field is empty',
            'category_name.unique' =>  'this category already exist'
        ]);

        $category = new Category;
        $category->category_name = $request->category_name;
        $category->save();

        return redirect()->route('categories')->with('success', 'the category is added succefully');
    }
    public function updateCategory(Request $request, $id){
        $request->validate([
            'category_name' => 'required|string|unique:categories,category_name'
        ]);
    
        $category = Category::findOrFail($id);
        $category->update([
            'category_name' => $request->category_name
        ]);
        
        return redirect()->back()->with('success', 'Category updated successfully!');
    }
    public function deleteCategory($id){
        $category = Category::find($id);
        $category->delete();
        return redirect()->back()->with('success', 'Category deleted successfully');;
    }
}
